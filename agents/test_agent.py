"""
Test Agent - Automated testing and validation
"""
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TestAgent:
    """Agent for automated testing and validation"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.test_results = []
        
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": []
        }
        
        # Check orchestrator
        check = await self._check_orchestrator()
        results["checks"].append(check)
        
        # Check runtimes
        for runtime_name in self.orchestrator.runtimes.keys():
            check = await self._check_runtime(runtime_name)
            results["checks"].append(check)
        
        # Check models
        check = await self._check_models()
        results["checks"].append(check)
        
        # Check resources
        check = await self._check_resources()
        results["checks"].append(check)
        
        # Determine overall status
        if any(c["status"] == "failed" for c in results["checks"]):
            results["overall_status"] = "unhealthy"
        elif any(c["status"] == "warning" for c in results["checks"]):
            results["overall_status"] = "degraded"
        
        return results
    
    async def _check_orchestrator(self) -> Dict[str, Any]:
        """Check orchestrator health"""
        
        try:
            health = await self.orchestrator.get_health_status()
            
            return {
                "component": "orchestrator",
                "status": "passed" if health["status"] == "healthy" else "failed",
                "details": health
            }
        except Exception as e:
            return {
                "component": "orchestrator",
                "status": "failed",
                "error": str(e)
            }
    
    async def _check_runtime(self, runtime_name: str) -> Dict[str, Any]:
        """Check runtime health"""
        
        try:
            runtime = self.orchestrator.runtimes.get(runtime_name)
            if not runtime:
                return {
                    "component": f"runtime_{runtime_name}",
                    "status": "failed",
                    "error": "Runtime not found"
                }
            
            is_healthy = await runtime.health_check()
            
            return {
                "component": f"runtime_{runtime_name}",
                "status": "passed" if is_healthy else "failed",
                "details": {"healthy": is_healthy}
            }
        except Exception as e:
            return {
                "component": f"runtime_{runtime_name}",
                "status": "failed",
                "error": str(e)
            }
    
    async def _check_models(self) -> Dict[str, Any]:
        """Check model availability"""
        
        try:
            models = self.orchestrator.registry.list_models()
            
            return {
                "component": "models",
                "status": "passed" if len(models) > 0 else "warning",
                "details": {
                    "total_models": len(models),
                    "models": models
                }
            }
        except Exception as e:
            return {
                "component": "models",
                "status": "failed",
                "error": str(e)
            }
    
    async def _check_resources(self) -> Dict[str, Any]:
        """Check resource availability"""
        
        try:
            resources = await self.orchestrator._get_resource_usage()
            
            warnings = []
            
            if resources["cpu_percent"] > 90:
                warnings.append("High CPU usage")
            
            if resources["memory_percent"] > 90:
                warnings.append("High memory usage")
            
            if resources["disk_percent"] > 90:
                warnings.append("High disk usage")
            
            status = "passed"
            if warnings:
                status = "warning"
            
            return {
                "component": "resources",
                "status": status,
                "warnings": warnings,
                "details": resources
            }
        except Exception as e:
            return {
                "component": "resources",
                "status": "failed",
                "error": str(e)
            }
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        
        test_suite = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test 1: Simple inference
        test = await self._test_simple_inference()
        test_suite["tests"].append(test)
        test_suite["total_tests"] += 1
        if test["status"] == "passed":
            test_suite["passed"] += 1
        else:
            test_suite["failed"] += 1
        
        # Test 2: Code generation
        test = await self._test_code_generation()
        test_suite["tests"].append(test)
        test_suite["total_tests"] += 1
        if test["status"] == "passed":
            test_suite["passed"] += 1
        else:
            test_suite["failed"] += 1
        
        # Test 3: Model switching
        test = await self._test_model_switching()
        test_suite["tests"].append(test)
        test_suite["total_tests"] += 1
        if test["status"] == "passed":
            test_suite["passed"] += 1
        else:
            test_suite["failed"] += 1
        
        # Test 4: Error handling
        test = await self._test_error_handling()
        test_suite["tests"].append(test)
        test_suite["total_tests"] += 1
        if test["status"] == "passed":
            test_suite["passed"] += 1
        else:
            test_suite["failed"] += 1
        
        # Test 5: Concurrent requests
        test = await self._test_concurrent_requests()
        test_suite["tests"].append(test)
        test_suite["total_tests"] += 1
        if test["status"] == "passed":
            test_suite["passed"] += 1
        else:
            test_suite["failed"] += 1
        
        return test_suite
    
    async def _test_simple_inference(self) -> Dict[str, Any]:
        """Test simple inference"""
        
        try:
            result = await self.orchestrator.run_inference(
                prompt="Say hello",
                task_type="chat"
            )
            
            if result and "output" in result and len(result["output"]) > 0:
                return {
                    "test": "simple_inference",
                    "status": "passed",
                    "details": {
                        "model": result.get("model"),
                        "processing_time": result.get("processing_time")
                    }
                }
            else:
                return {
                    "test": "simple_inference",
                    "status": "failed",
                    "error": "No output generated"
                }
        except Exception as e:
            return {
                "test": "simple_inference",
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_code_generation(self) -> Dict[str, Any]:
        """Test code generation"""
        
        try:
            result = await self.orchestrator.run_inference(
                prompt="Write a Python function to add two numbers",
                task_type="code_generation"
            )
            
            output = result.get("output", "")
            
            # Check if output contains code indicators
            has_code = "def" in output or "function" in output.lower()
            
            if has_code:
                return {
                    "test": "code_generation",
                    "status": "passed",
                    "details": {
                        "model": result.get("model"),
                        "output_length": len(output)
                    }
                }
            else:
                return {
                    "test": "code_generation",
                    "status": "failed",
                    "error": "Output doesn't appear to contain code"
                }
        except Exception as e:
            return {
                "test": "code_generation",
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_model_switching(self) -> Dict[str, Any]:
        """Test switching between models"""
        
        try:
            models = self.orchestrator.registry.list_models()
            
            if len(models) < 2:
                return {
                    "test": "model_switching",
                    "status": "skipped",
                    "reason": "Less than 2 models available"
                }
            
            # Test with first model
            result1 = await self.orchestrator.run_inference(
                prompt="Test",
                model=models[0]
            )
            
            # Test with second model
            result2 = await self.orchestrator.run_inference(
                prompt="Test",
                model=models[1]
            )
            
            if result1.get("model") != result2.get("model"):
                return {
                    "test": "model_switching",
                    "status": "passed",
                    "details": {
                        "model1": result1.get("model"),
                        "model2": result2.get("model")
                    }
                }
            else:
                return {
                    "test": "model_switching",
                    "status": "failed",
                    "error": "Models didn't switch"
                }
        except Exception as e:
            return {
                "test": "model_switching",
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling"""
        
        try:
            # Try with invalid model
            try:
                await self.orchestrator.run_inference(
                    prompt="Test",
                    model="nonexistent-model"
                )
                return {
                    "test": "error_handling",
                    "status": "failed",
                    "error": "Should have raised error for invalid model"
                }
            except Exception:
                # Expected to fail
                return {
                    "test": "error_handling",
                    "status": "passed",
                    "details": "Correctly handled invalid model"
                }
        except Exception as e:
            return {
                "test": "error_handling",
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_concurrent_requests(self) -> Dict[str, Any]:
        """Test concurrent request handling"""
        
        try:
            # Send 3 concurrent requests
            tasks = [
                self.orchestrator.run_inference(
                    prompt=f"Test {i}",
                    task_type="chat"
                )
                for i in range(3)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if all succeeded
            successful = sum(
                1 for r in results
                if isinstance(r, dict) and "output" in r
            )
            
            if successful == 3:
                return {
                    "test": "concurrent_requests",
                    "status": "passed",
                    "details": {
                        "total_requests": 3,
                        "successful": successful
                    }
                }
            else:
                return {
                    "test": "concurrent_requests",
                    "status": "failed",
                    "error": f"Only {successful}/3 requests succeeded"
                }
        except Exception as e:
            return {
                "test": "concurrent_requests",
                "status": "failed",
                "error": str(e)
            }
    
    async def benchmark_performance(
        self,
        num_requests: int = 10
    ) -> Dict[str, Any]:
        """Benchmark system performance"""
        
        start_time = datetime.now()
        
        results = {
            "timestamp": start_time.isoformat(),
            "num_requests": num_requests,
            "results": []
        }
        
        for i in range(num_requests):
            request_start = datetime.now()
            
            try:
                result = await self.orchestrator.run_inference(
                    prompt="Benchmark test",
                    task_type="quick_query"
                )
                
                request_time = (datetime.now() - request_start).total_seconds()
                
                results["results"].append({
                    "request_id": i,
                    "status": "success",
                    "processing_time": request_time,
                    "tokens": result.get("tokens_used", 0)
                })
            except Exception as e:
                results["results"].append({
                    "request_id": i,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Calculate statistics
        successful = [r for r in results["results"] if r["status"] == "success"]
        
        if successful:
            times = [r["processing_time"] for r in successful]
            
            results["statistics"] = {
                "total_time": (datetime.now() - start_time).total_seconds(),
                "successful_requests": len(successful),
                "failed_requests": num_requests - len(successful),
                "avg_processing_time": sum(times) / len(times),
                "min_processing_time": min(times),
                "max_processing_time": max(times),
                "requests_per_second": len(successful) / (datetime.now() - start_time).total_seconds()
            }
        
        return results