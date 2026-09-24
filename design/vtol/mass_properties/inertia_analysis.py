from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class InertiaTensor:
    """
    Aircraft moments and cross-products of inertia.
    """
    ixx_kg_m2: float
    iyy_kg_m2: float
    izz_kg_m2: float
    ixy_kg_m2: float
    ixz_kg_m2: float
    iyz_kg_m2: float
    metadata: Dict[str, Any] = field(default_factory=dict)
