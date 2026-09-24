from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .weight_budget import WeightBudget
from .mass_distribution import MassDistribution
from .cg_analysis import CenterOfGravity, CGEnvelope
from .inertia_analysis import InertiaTensor
from .payload_shift_analysis import PayloadShiftAnalysis
from .battery_shift_analysis import BatteryShiftAnalysis
from .mass_properties_analysis import MassPropertiesAnalysis

if TYPE_CHECKING:
    from .authoritative_mass import AuthoritativeMassResult

@dataclass(slots=True)
class MassResult:
    """
    Consolidated output of the VTOL Mass Properties and Center of Gravity sizing.
    """
    weight_budget: WeightBudget
    mass_distribution: MassDistribution
    center_of_gravity: CenterOfGravity
    cg_envelope: CGEnvelope
    inertia_tensor: InertiaTensor
    payload_shift_analysis: PayloadShiftAnalysis
    battery_shift_analysis: BatteryShiftAnalysis
    mass_analysis: MassPropertiesAnalysis

    authoritative_mass_result: Optional[Any] = None
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes mass result to JSON-compatible dictionary."""
        d: Dict[str, Any] = {
            "weight_budget": {
                "max_takeoff_weight_kg": self.weight_budget.max_takeoff_weight_kg,
                "empty_weight_kg": self.weight_budget.empty_weight_kg,
                "payload_mass_kg": self.weight_budget.payload_mass_kg,
            },
            "center_of_gravity": {
                "x_m": self.center_of_gravity.x_m,
                "y_m": self.center_of_gravity.y_m,
                "z_m": self.center_of_gravity.z_m,
                "x_pct_mac": self.center_of_gravity.x_pct_mac,
            },
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }
        if self.authoritative_mass_result is not None and hasattr(self.authoritative_mass_result, "to_dict"):
            d["authoritative_mass_result"] = self.authoritative_mass_result.to_dict()
        return d
