import asyncio
import os
import shutil
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

from services.build_service import BuildService
from services.runtime_service import RuntimeService

async def test_execution_flow():
    print("Testing Project Build and Execution Flow...")
    
    # 1. Setup a dummy project
    project_path = Path("temp_test_project")
    if project_path.exists():
        shutil.rmtree(project_path)
    project_path.mkdir()
    
    with open(project_path / "app.py", "w") as f:
        f.write("import time\nprint('Starting app...')\ntime.sleep(2)\nprint('App running!')\n")
        
    with open(project_path / "requirements.txt", "w") as f:
        f.write("# No dependencies\n")
        
    print(f"Created dummy project at {project_path}")
    
    # 2. Test Build
    build_service = BuildService()
    print("Running build...")
    build_res = await build_service.build_project(str(project_path))
    print(f"Build Result: {build_res['success']}, Message: {build_res.get('message', '')}")
    
    if not build_res['success']:
        print(f"Build failed: {build_res.get('error')}")
        return

    # 3. Test Run
    runtime_service = RuntimeService()
    print("Starting app...")
    run_res = await runtime_service.start_project(
        project_id="test-p1",
        local_path=str(project_path),
        config={"command": ["python", "app.py"]}
    )
    
    print(f"Run Result: {run_res['success']}, Message: {run_res.get('message', '')}")
    if run_res['success']:
        print(f"App PID: {run_res.get('pid')}")
        
        # Wait a bit for output
        await asyncio.sleep(3)
        
        # 4. Test Logs
        print("Retrieving logs...")
        logs = await runtime_service.get_logs("test-p1")
        print(f"Logs:\n{logs}")
        
        # 5. Test Stop
        print("Stopping app...")
        stop_res = await runtime_service.stop_project("test-p1")
        print(f"Stop Result: {stop_res['success']}, Message: {stop_res['message']}")

    # Cleanup
    if project_path.exists():
        shutil.rmtree(project_path)
    print("Test Complete.")

if __name__ == "__main__":
    asyncio.run(test_execution_flow())
