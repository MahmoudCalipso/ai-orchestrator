"""
Figma API Client
"""
import os
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class FigmaClient:
    """Client for interactions with Figma API"""
    
    BASE_URL = "https://api.figma.com/v1"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("FIGMA_API_TOKEN")
        if not self.token:
            logger.warning("Figma API token not provided")
            
    @property
    def headers(self):
        return {
            "X-Figma-Token": self.token,
            "Content-Type": "application/json"
        }
        
    async def get_file(self, file_key: str) -> Dict[str, Any]:
        """Get file content from Figma"""
        if not self.token:
            raise ValueError("Figma API token required")
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/files/{file_key}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
            
    async def get_image_urls(self, file_key: str, node_ids: str, format: str = "png") -> Dict[str, Any]:
        """Get image URLs for nodes"""
        if not self.token:
            raise ValueError("Figma API token required")
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/images/{file_key}",
                params={"ids": node_ids, "format": format},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
