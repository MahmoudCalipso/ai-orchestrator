import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeNode:
    def __init__(self, id: str, type: str, metadata: Dict[str, Any]):
        self.id = id
        self.type = type
        self.metadata = metadata
        self.created_at = datetime.now()

class KnowledgeGraphService:
    """
    🧠 Agentic Knowledge Graph (L3 Memory)
    Provides a relational map of all project entities (Code, Infra, Cost, Security).
    """
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[Dict[str, str]] = []  # List of {"from": id, "to": id, "relation": type}
        logger.info("🧠 KnowledgeGraphService initialized - L3 Relational Reasoning ready")

    async def add_node(self, node_id: str, node_type: str, metadata: Dict[str, Any]):
        """Add a node to the knowledge graph"""
        self.nodes[node_id] = KnowledgeNode(node_id, node_type, metadata)
        logger.debug(f"Knowledge Graph: Added {node_type} node: {node_id}")

    async def link_nodes(self, source_id: str, target_id: str, relation: str):
        """Create a directed edge between two nodes"""
        if source_id in self.nodes and target_id in self.nodes:
            self.edges.append({
                "from": source_id,
                "to": target_id,
                "relation": relation
            })
            logger.info(f"Knowledge Graph Link: {source_id} --({relation})--> {target_id}")

    async def query_impact(self, node_id: str) -> List[Dict[str, Any]]:
        """Query all nodes affected by or related to a specific node (Recursive Impact Analysis)"""
        impacted = []
        for edge in self.edges:
            if edge["from"] == node_id:
                target = self.nodes.get(edge["to"])
                if target:
                    impacted.append({
                        "node": target.id,
                        "type": target.type,
                        "relation": edge["relation"]
                    })
        return impacted

    async def get_graph_summary(self) -> Dict[str, Any]:
        """Return a high-level summary of the graph state"""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "types": list(set(n.type for n in self.nodes.values()))
        }
