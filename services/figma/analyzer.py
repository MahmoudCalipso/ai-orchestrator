"""
Figma Design Analyzer
"""
import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DesignToken(BaseModel):
    name: str # e.g. "Primary Color"
    value: str # e.g. "#FF0000" or "Inter, 16px"
    type: str # color, typography, spacing

class DesignComponent(BaseModel):
    id: str
    name: str
    type: str # FRAME, INSTANCE, COMPONENT
    properties: Dict[str, Any]
    children: List['DesignComponent'] = []

class FigmaAnalyzer:
    """Analyzes Figma files to extract design system and components using AI Intelligence"""
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator

    async def analyze_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze full Figma file using AI for rich interpretation.
        """
        logger.info(f"🚀 AI Power-Up: Analyzing Figma Design '{file_data.get('name')}'")
        
        if not self.orchestrator:
            # Fallback for simple extraction if no AI is available
            return self._extract_legacy(file_data)

        # Construct task for the AI Agent to perform forensic analysis of the Figma JSON
        task = "Perform a deep design audit of this Figma document structure."
        context = {
            "type": "figma_analysis",
            "document_name": file_data.get("name"),
            "file_data": file_data, # Pass a truncated version or specific nodes if too large
            "requirements": "Extract design tokens (colors, typography, spacing) and high-level component structures."
        }

        try:
            result = await self.orchestrator.universal_agent.act(task, context)
            solution = result.get("solution", "")
            
            # The AI returns an intelligent interpretation of the design
            return {
                "status": "success",
                "ai_interpretation": solution,
                "document_name": file_data.get("name"),
                "timestamp": file_data.get("lastModified")
            }
        except Exception as e:
            logger.error(f"AI Figma analysis failed: {e}")
            return self._extract_legacy(file_data)

    def _extract_legacy(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy fall-back logic for basic extraction"""
        document = file_data.get("document", {})
        return {
            "styles": [],
            "components": [],
            "name": file_data.get("name"),
            "warning": "Initial AI analysis failed, used legacy extraction."
        }
