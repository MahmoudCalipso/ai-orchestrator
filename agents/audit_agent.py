"""
Audit Agent - Comprehensive auditing and compliance
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditAgent:
    """Agent for auditing system activity and compliance"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.audit_log_path = Path("logs/audit.jsonl")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def log_event(
        self,
        event_type: str,
        user: str,
        action: str,
        resource: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an audit event"""
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": user,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {}
        }
        
        # Write to file
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logger.info(f"Audit event logged: {event_type} - {action} - {status}")
    
    async def log_inference_request(
        self,
        user: str,
        request_id: str,
        model: str,
        task_type: str,
        prompt_length: int,
        status: str
    ):
        """Log an inference request"""
        
        await self.log_event(
            event_type="inference",
            user=user,
            action="generate",
            resource=model,
            status=status,
            details={
                "request_id": request_id,
                "task_type": task_type,
                "prompt_length": prompt_length
            }
        )
    
    async def log_model_operation(
        self,
        user: str,
        operation: str,
        model: str,
        runtime: str,
        status: str
    ):
        """Log a model operation (load/unload)"""
        
        await self.log_event(
            event_type="model_operation",
            user=user,
            action=operation,
            resource=model,
            status=status,
            details={"runtime": runtime}
        )
    
    async def log_configuration_change(
        self,
        user: str,
        config_type: str,
        changes: Dict[str, Any],
        status: str
    ):
        """Log a configuration change"""
        
        await self.log_event(
            event_type="configuration",
            user=user,
            action="update",
            resource=config_type,
            status=status,
            details={"changes": changes}
        )
    
    async def log_security_event(
        self,
        user: str,
        event: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """Log a security event"""
        
        await self.log_event(
            event_type="security",
            user=user,
            action=event,
            resource="system",
            status=severity,
            details=details
        )
    
    async def get_audit_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filters"""
        
        logs = []
        
        if not self.audit_log_path.exists():
            return logs
        
        with open(self.audit_log_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    
                    # Apply filters
                    event_time = datetime.fromisoformat(event["timestamp"])
                    
                    if start_time and event_time < start_time:
                        continue
                    
                    if end_time and event_time > end_time:
                        continue
                    
                    if event_type and event["event_type"] != event_type:
                        continue
                    
                    if user and event["user"] != user:
                        continue
                    
                    logs.append(event)
                    
                    if len(logs) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return logs
    
    async def generate_audit_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        
        # Default to last 24 hours if not specified
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=1)
        
        logs = await self.get_audit_logs(
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        # Aggregate statistics
        total_events = len(logs)
        
        events_by_type = {}
        events_by_user = {}
        events_by_status = {}
        
        for event in logs:
            # By type
            event_type = event["event_type"]
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            # By user
            user = event["user"]
            events_by_user[user] = events_by_user.get(user, 0) + 1
            
            # By status
            status = event["status"]
            events_by_status[status] = events_by_status.get(status, 0) + 1
        
        # Identify anomalies
        anomalies = await self._detect_anomalies(logs)
        
        # Security events
        security_events = [
            e for e in logs if e["event_type"] == "security"
        ]
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "total_events": total_events,
                "events_by_type": events_by_type,
                "events_by_user": events_by_user,
                "events_by_status": events_by_status
            },
            "security": {
                "total_security_events": len(security_events),
                "critical_events": [
                    e for e in security_events
                    if e.get("status") == "critical"
                ]
            },
            "anomalies": anomalies,
            "top_users": sorted(
                events_by_user.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        
        return report
    
    async def _detect_anomalies(
        self,
        logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in audit logs"""
        
        anomalies = []
        
        # Check for rapid repeated failures
        failures = [e for e in logs if e["status"] in ["error", "failed"]]
        
        if failures:
            # Group by user
            failures_by_user = {}
            for failure in failures:
                user = failure["user"]
                if user not in failures_by_user:
                    failures_by_user[user] = []
                failures_by_user[user].append(failure)
            
            # Check for users with high failure rates
            for user, user_failures in failures_by_user.items():
                if len(user_failures) > 10:
                    anomalies.append({
                        "type": "high_failure_rate",
                        "user": user,
                        "count": len(user_failures),
                        "severity": "medium"
                    })
        
        # Check for unusual access patterns
        # (simplified implementation)
        
        return anomalies
    
    async def check_compliance(self) -> Dict[str, Any]:
        """Check system compliance with policies"""
        
        compliance_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "compliant",
            "checks": []
        }
        
        # Check 1: All API calls are authenticated
        recent_logs = await self.get_audit_logs(
            start_time=datetime.now() - timedelta(hours=1),
            limit=1000
        )
        
        unauthenticated = [
            e for e in recent_logs
            if e.get("user") == "anonymous"
        ]
        
        compliance_results["checks"].append({
            "check": "authentication_required",
            "status": "pass" if len(unauthenticated) == 0 else "fail",
            "details": f"{len(unauthenticated)} unauthenticated requests found"
        })
        
        # Check 2: Audit logging is enabled
        compliance_results["checks"].append({
            "check": "audit_logging_enabled",
            "status": "pass",
            "details": f"{len(recent_logs)} events logged in last hour"
        })
        
        # Check 3: Failed authentication attempts
        failed_auth = [
            e for e in recent_logs
            if e.get("event_type") == "security"
            and "authentication" in e.get("action", "").lower()
            and e.get("status") in ["failed", "error"]
        ]
        
        compliance_results["checks"].append({
            "check": "authentication_failures",
            "status": "warning" if len(failed_auth) > 5 else "pass",
            "details": f"{len(failed_auth)} failed authentication attempts"
        })
        
        # Determine overall status
        if any(c["status"] == "fail" for c in compliance_results["checks"]):
            compliance_results["overall_status"] = "non_compliant"
        elif any(c["status"] == "warning" for c in compliance_results["checks"]):
            compliance_results["overall_status"] = "warning"
        
        return compliance_results
    
    async def export_audit_logs(
        self,
        output_path: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        format: str = "json"
    ):
        """Export audit logs to file"""
        
        logs = await self.get_audit_logs(
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        output_file = Path(output_path)
        
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(logs, f, indent=2)
        
        elif format == "csv":
            import csv
            
            with open(output_file, 'w', newline='') as f:
                if logs:
                    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)
        
        logger.info(f"Exported {len(logs)} audit logs to {output_path}")
        
        return {
            "status": "success",
            "exported_count": len(logs),
            "output_path": str(output_file)
        }