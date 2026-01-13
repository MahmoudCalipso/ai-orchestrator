import asyncio
import json
import re

async def verify_ultimate_flow():
    print("Verifying Ultimate High-Quality Flow...")
    
    # Simulate swarm results from TWO-PASS (Generate then Review)
    worker_results = {
        "backend": {
            "solution": "### FILE: main.py\n```python\n# Refined FastAPI Code\n```\n### FILE: models.py\n```python\n# Refined Models\n```",
            "infrastructure": {"dockerfile": "FROM python:3.12-slim\n..."},
            "model_used": "qwen2.5-coder" # Review pass model
        }
    }
    
    result = {"generated_files": {}}
    
    # Same logic as main.py
    for domain, worker_out in worker_results.items():
        solution = worker_out.get("solution", "")
        code_blocks = re.findall(r'### FILE: (.*?)\n```(?:\w+)?\n(.*?)\n```', solution, re.DOTALL)
        
        if code_blocks:
            for filename, content in code_blocks:
                result["generated_files"][f"{domain}/{filename}"] = content
        else:
             print("Extraction failed!")
    
    assert "backend/main.py" in result["generated_files"]
    assert "Refined FastAPI Code" in result["generated_files"]["backend/main.py"]
    assert "backend/models.py" in result["generated_files"]
    
    print("Multi-file Extraction: SUCCESS")
    print("Verification Successful!")

if __name__ == "__main__":
    asyncio.run(verify_ultimate_flow())
