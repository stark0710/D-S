"""
Fixed-Wing Aircraft Convergence Models
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class ConvergenceTolerances:
    """Configurable convergence tolerances for monitored variables."""
    mtow: float = 0.05            # absolute tolerance in kg
    wing_area: float = 0.005      # absolute tolerance in m^2
    wing_loading: float = 0.2     # absolute tolerance in kg/m^2
    battery_mass: float = 0.02    # absolute tolerance in kg
    empty_weight: float = 0.05    # absolute tolerance in kg
    cg_x: float = 0.005           # absolute tolerance in m
    static_margin: float = 0.005  # absolute tolerance (0.5% margin)
    cruise_power: float = 2.0     # absolute tolerance in W
    endurance: float = 0.5        # absolute tolerance in minutes
    range: float = 0.2            # absolute tolerance in km


@dataclass(slots=True)
class FinalAircraftSpecification:
    """
    Consolidated engineering specification of the converged aircraft system.
    """
    mission_summary: Dict[str, Any]
    wing_specification: Any
    fuselage_specification: Any
    payload_specification: Any
    tail_specification: Any
    propulsion_specification: Any
    electrical_specification: Any
    mass_properties_specification: Any
    cg_specification: Any
    performance_specification: Any
    iteration_history: List[Dict[str, Any]]
    convergence_status: str
    final_design_score: float
