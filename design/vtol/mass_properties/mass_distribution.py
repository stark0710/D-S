from dataclasses import dataclass, field
from typing import List, Dict, Any
from .component_mass import ComponentMass

@dataclass(slots=True)
class MassDistribution:
    """
    Aggregated components list and center of gravity distributions.
    """
    components: List[ComponentMass]
    mass_concentration_factor: float  # radius of gyration check
    metadata: Dict[str, Any] = field(default_factory=dict)
