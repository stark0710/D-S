"""
Fixed-Wing Propulsion Efficiency Analysis Subsystem

Purpose:
    Defines the `EfficiencyAnalysis` class and sizing calculations.

Role in Architecture:
    `EfficiencyAnalysis` evaluates motor/engine thermal efficiency, propeller blade slip,
    and total combined powertrain efficiency.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class EfficiencyAnalysis:
    """
    Powertrain energy conversion efficiencies.

    Attributes:
        motor_efficiency (float): Sized electrical efficiency factor (0.0 to 1.0).
        propeller_efficiency (float): Sized aerodynamic efficiency factor (0.0 to 1.0).
        total_system_efficiency (float): Combined efficiency factor (motor * propeller).
        energy_consumption_per_km_wh (float): Sized energy depletion rate per kilometer of range.
        metadata (Dict[str, Any]): Intermediate pitch slip and drag torque.
    """

    motor_efficiency: float
    propeller_efficiency: float
    total_system_efficiency: float
    energy_consumption_per_km_wh: float
    metadata: Dict[str, Any] = field(default_factory=dict)
