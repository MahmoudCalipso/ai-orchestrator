"""
Figma Design Analyzer
"""
import logging
from typing import Dict, Any, List, Optional
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
    """Analyzes Figma files to extract design system and components"""
    
    def analyze_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze full Figma file"""
        document = file_data.get("document", {})
        
        styles = self._extract_styles(file_data)
        components = self._extract_components(document)
        
        return {
            "styles": styles,
            "components": components,
            "name": file_data.get("name")
        }
    
    def _extract_styles(self, file_data: Dict[str, Any]) -> List[DesignToken]:
        """Extract styles/tokens"""
        # Placeholder for complex style extraction logic
        # Would parse styles map from file_data["styles"]
        return []
        
    def _extract_components(self, node: Dict[str, Any]) -> List[DesignComponent]:
        """Recursively extract components"""
        components = []
        
        node_type = node.get("type")
        if node_type == "COMPONENT" or (node_type == "FRAME" and node.get("name", "").startswith("#")):
            # It's a component or designated frame
            comp = DesignComponent(
                id=node.get("id"),
                name=node.get("name"),
                type=node_type,
                properties=self._extract_properties(node)
            )
            # Scan children
            if "children" in node:
                for child in node["children"]:
                    comp.children.extend(self._extract_components(child))
            
            # Don't return the component itself if it's nested (unless root), 
            # here we return a flat list of found high-level components for simplicity
            return [comp] 
            
        # Continue recursion
        if "children" in node:
            for child in node["children"]:
                components.extend(self._extract_components(child))
                
        return components

    def _extract_properties(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract CSS-relevant properties"""
        props = {}
        # Size
        if "absoluteBoundingBox" in node:
            box = node["absoluteBoundingBox"]
            props["width"] = box.get("width")
            props["height"] = box.get("height")
            
        # Color (fills)
        if "fills" in node:
            for fill in node["fills"]:
                if fill.get("type") == "SOLID" and fill.get("visible", True):
                    color = fill.get("color")
                    # Convert 0-1 RGB to Hex
                    props["background-color"] = self._rgb_to_hex(color)
                    
        return props
        
    def _rgb_to_hex(self, color: Dict[str, float]) -> str:
        r = int(color.get("r", 0) * 255)
        g = int(color.get("g", 0) * 255)
        b = int(color.get("b", 0) * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
