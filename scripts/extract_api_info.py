import json
import logging
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

# Create a dummy .env if missing to prevent startup errors
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("JWT_SECRET=test\n")

# Mock missing dependencies
from unittest.mock import MagicMock
sys.modules["motor"] = MagicMock()
sys.modules["motor.motor_asyncio"] = MagicMock()
sys.modules["pymongo"] = MagicMock()
sys.modules["qdrant_client"] = MagicMock()
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()

try:
    from main import app
    from starlette.routing import WebSocketRoute
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

def extract_info():
    print("Generating OpenAPI Schema...")
    # 1. Standard OpenAPI JSON
    openapi_schema = app.openapi()
    
    # 2. Manual WebSocket Extraction
    ws_endpoints = []
    for route in app.routes:
        if isinstance(route, WebSocketRoute):
            ws_endpoints.append({
                "path": route.path,
                "name": route.name,
                "tags": getattr(route, "tags", []),
                "description": route.path  # WS routes might not have docstrings exposed this way easily
            })
            
    # Inject WS info into OpenAPI extension
    openapi_schema["x-websockets"] = ws_endpoints
    
    output_file = "openapi_full.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
        
    print(f"Success! Exported to {output_file}")
    print(f"- REST Endpoints: {len(openapi_schema['paths'])}")
    print(f"- WebSocket Endpoints: {len(ws_endpoints)}")

if __name__ == "__main__":
    extract_info()
