"""
Fixed-Wing Aircraft Design Snapshot
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass(slots=True)
class DesignSnapshot:
    iteration: int
    mtow: float
    wing_area: float
    wing_loading: float
    battery_mass: float
    empty_weight: float
    cg_x: float
    static_margin: float
    cruise_power: float
    endurance: float
    range: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_snapshot(iteration: int, specs: Dict[str, Any]) -> DesignSnapshot:
    """Creates a DesignSnapshot from active subsystem specification outputs."""
    wing = specs.get("WingPlanformSpecification") or specs.get("WingPlanformOptimizer")
    prop = specs.get("PropulsionSpecification") or specs.get("PropulsionOptimizer")
    mass = specs.get("MassPropertiesSpecification") or specs.get("MassPropertiesOptimizer")
    cg = specs.get("CGSpecification") or specs.get("CGOptimizer")
    perf = specs.get("FlightPerformanceSpecification") or specs.get("FlightPerformanceOptimizer")

    return DesignSnapshot(
        iteration=iteration,
        mtow=getattr(mass, "maximum_takeoff_weight_kg", 0.0) if mass else 0.0,
        wing_area=getattr(wing, "wing_area", getattr(wing, "area_m2", 0.0)) if wing else 0.0,
        wing_loading=getattr(wing, "wing_loading", 0.0) if wing else 0.0,
        battery_mass=(getattr(prop, "battery_weight_g", 0.0) / 1000.0) if prop else 0.0,
        empty_weight=getattr(mass, "empty_weight_kg", 0.0) if mass else 0.0,
        cg_x=getattr(cg, "cg_position", (0.0, 0.0, 0.0))[0] if cg else 0.0,
        static_margin=getattr(cg, "static_margin", 0.0) if cg else 0.0,
        cruise_power=getattr(prop, "cruise_power_w", 0.0) if prop else 0.0,
        endurance=getattr(perf, "endurance_min", 0.0) if perf else 0.0,
        range=getattr(perf, "range_km", 0.0) if perf else 0.0,
    )
