from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(slots=True)
class WeightBudget:
    """
    Summarizes structural mass budgets.
    """
    wing_structure_mass_kg: float
    fuselage_structure_mass_kg: float
    tail_structure_mass_kg: float
    propulsion_system_mass_kg: float
    electrical_system_mass_kg: float
    avionics_system_mass_kg: float
    payload_mass_kg: float
    empty_weight_kg: float
    max_takeoff_weight_kg: float
    reserve_margin_kg: float
    weight_growth_margin_pct: float
    metadata: Dict[str, Any] = field(default_factory=dict)
