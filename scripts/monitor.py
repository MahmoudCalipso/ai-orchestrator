#!/usr/bin/env python3
"""
Monitoring script for AI Orchestrator
"""
import requests
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any


class OrchestratorMonitor:
    """Monitor for AI Orchestrator"""
    
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = None):
        self.base_url = base_url
        # Require API key from parameter or environment
        if not api_key:
            api_key = os.getenv("ORCHESTRATOR_API_KEY")
        if not api_key:
            raise ValueError("API key required. Set ORCHESTRATOR_API_KEY environment variable or pass --api-key")
        self.headers = {"X-API-Key": api_key}
        
    def check_health(self) -> Dict[str, Any]:
        """Check orchestrator health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return {
                "status": "ok" if response.status_code == 200 else "error",
                "data": response.json() if response.status_code == 200 else None,
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        try:
            response = requests.get(
                f"{self.base_url}/status",
                headers=self.headers,
                timeout=5
            )
            return {
                "status": "ok" if response.status_code == 200 else "error",
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics"""
        try:
            response = requests.get(
                f"{self.base_url}/metrics",
                headers=self.headers,
                timeout=5
            )
            return {
                "status": "ok" if response.status_code == 200 else "error",
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def print_dashboard(self):
        """Print monitoring dashboard"""
        # Clear screen
        print("\033[2J\033[H")
        
        print("=" * 80)
        print(f"AI ORCHESTRATOR MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Health check
        print("\n[HEALTH CHECK]")
        health = self.check_health()
        if health["status"] == "ok":
            data = health["data"]
            print(f"✓ Status: {data['status']}")
            print(f"✓ Uptime: {data['uptime']:.2f}s")
            print(f"✓ Models loaded: {data['models_loaded']}")
            print(f"✓ Runtimes: {', '.join(data['runtimes_available'])}")
        else:
            print(f"✗ Error: {health.get('error', 'Unknown error')}")
        
        # System status
        print("\n[SYSTEM STATUS]")
        status = self.get_status()
        if status["status"] == "ok":
            data = status["data"]
            resources = data.get("resources", {})
            
            print(f"CPU Usage: {resources.get('cpu_percent', 0):.1f}%")
            print(f"Memory Usage: {resources.get('memory_percent', 0):.1f}%")
            print(f"Disk Usage: {resources.get('disk_percent', 0):.1f}%")
            
            gpus = resources.get("gpus", [])
            if gpus:
                print("\nGPU Status:")
                for gpu in gpus:
                    print(f"  {gpu['name']}: {gpu['load']:.1f}% load, "
                          f"{gpu['memory_used']}MB/{gpu['memory_total']}MB "
                          f"({gpu['temperature']}°C)")
        else:
            print(f"✗ Error: {status.get('error', 'Unknown error')}")
        
        # Metrics
        print("\n[METRICS]")
        metrics = self.get_metrics()
        if metrics["status"] == "ok":
            data = metrics["data"]
            print(f"Total Requests: {data.get('total_requests', 0)}")
            print(f"Successful: {data.get('successful_requests', 0)}")
            print(f"Failed: {data.get('failed_requests', 0)}")
            print(f"Success Rate: {data.get('success_rate', 0):.2%}")
            print(f"Avg Processing Time: {data.get('average_processing_time', 0):.2f}s")
            print(f"Total Tokens: {data.get('total_tokens', 0)}")
        else:
            print(f"✗ Error: {metrics.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print("Press Ctrl+C to exit")
    
    def run_continuous(self, interval: int = 5):
        """Run continuous monitoring"""
        print("Starting continuous monitoring...")
        print(f"Refresh interval: {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.print_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            sys.exit(0)
    
    def run_once(self):
        """Run monitoring once"""
        self.print_dashboard()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Orchestrator Monitor")
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Orchestrator URL"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (or set ORCHESTRATOR_API_KEY environment variable)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Refresh interval in seconds"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )
    
    args = parser.parse_args()
    
    try:
        monitor = OrchestratorMonitor(args.url, args.api_key)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.once:
        monitor.run_once()
    else:
        monitor.run_continuous(args.interval)


if __name__ == "__main__":
    main()