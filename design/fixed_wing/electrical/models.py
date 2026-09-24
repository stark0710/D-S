"""
Electrical System Specification Models

Defines the output specification dataclass for the electrical engine.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ElectricalSystemSpecification:
    """
    Final optimized electrical and avionics architecture parameters.
    """
    flight_controller_name: str
    gps_name: str
    compass_name: str
    telemetry_name: str
    receiver_name: str
    servo_name: str
    servo_count: int
    power_module_name: str
    bec_name: str
    power_distribution_layout: str
    wire_gauge_awg: int
    connector_type: str
    mission_equipment_name: str

    # Engineering metrics
    electrical_power_budget_w: float
    estimated_electrical_mass_g: float
    redundancy_level: int
    optimization_score: float
    reasoning: str
