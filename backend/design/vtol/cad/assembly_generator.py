from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(slots=True)
class AssemblyNode:
    """
    A node in the CAD assembly tree.
    """
    node_name: str
    child_nodes: List[str]
    mass_kg: float
    center_of_gravity_mm: List[float]

@dataclass(slots=True)
class AssemblyModel:
    """
    Complete hierarchy of part relations.
    """
    assembly_name: str
    nodes: List[AssemblyNode]
    total_parts_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
