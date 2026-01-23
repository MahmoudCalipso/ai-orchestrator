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
        Analyze full Figma file using AI for rich interpretation and specialized token extraction.
        """
        logger.info(f"🚀 AI Power-Up: Analyzing Figma Design '{file_data.get('name')}'")
        
        # 1. Specialized Token Extraction (Deterministic)
        tokens = self._extract_design_tokens(file_data)
        
        if not self.orchestrator:
            return {**self._extract_legacy(file_data), "tokens": tokens}

        # 2. AI Interpretation for layout and components
        task = "Perform a deep design audit of this Figma document structure."
        context = {
            "type": "figma_analysis",
            "document_name": file_data.get("name"),
            "extracted_tokens": tokens,
            "file_data": file_data, 
            "requirements": "Extract high-level component structures and map them to our Design System."
        }

        try:
            result = await self.orchestrator.universal_agent.act(task, context)
            solution = result.get("solution", "")
            
            return {
                "status": "success",
                "ai_interpretation": solution,
                "tokens": tokens,
                "document_name": file_data.get("name"),
                "timestamp": file_data.get("lastModified")
            }
        except Exception as e:
            logger.error(f"AI Figma analysis failed: {e}")
            return {**self._extract_legacy(file_data), "tokens": tokens}

    def _extract_design_tokens(self, file_data: Dict[str, Any]) -> List[DesignToken]:
        """Specialized logic to extract colors and typography from Figma styles"""
        tokens = []
        styles = file_data.get("styles", {})
        
        # This would iterate over styles and extract values
        # Simplified for now: assume we parse the document tree for 'color' and 'font' fills
        logger.info(f"Extracted {len(styles)} design styles from Figma metadata")
        
        for style_id, style_info in styles.items():
            tokens.append(DesignToken(
                name=style_info.get("name", "Unknown"),
                value="Extracted from Figma Style",
                type=style_info.get("styleType", "OTHER").lower()
            ))
            
        return tokens

    def _extract_legacy(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy fall-back logic for basic extraction"""
        document = file_data.get("document", {})
        return {
            "styles": [],
            "components": [],
            "name": file_data.get("name"),
            "warning": "Initial AI analysis failed, used legacy extraction."
        }
