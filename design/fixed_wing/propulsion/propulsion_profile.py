"""
Fixed-Wing Propulsion Sizing Profile Subsystem

Purpose:
    Defines the `PropulsionProfile` class, which holds safety factors and efficiency targets.

Role in Architecture:
    The profile is used to configure standard motor efficiency constants, propeller efficiency goals,
    and takeoff thrust safety factors.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PropulsionProfile:
    """
    Configuration profile defining limits and efficiencies for motor sizing.

    Attributes:
        min_thrust_to_weight_takeoff (float): Minimum takeoff thrust-to-weight ratio (default 0.45).
        min_thrust_to_weight_climb (float): Minimum climb thrust-to-weight ratio (default 0.35).
        default_motor_efficiency (float): Expected motor electrical efficiency (default 0.82).
        default_prop_efficiency (float): Expected propeller aerodynamic efficiency (default 0.65).
        air_viscosity_pa_s (float): Reference viscosity (default 1.7894e-5).
    """

    min_thrust_to_weight_takeoff: float = 0.45
    min_thrust_to_weight_climb: float = 0.35
    default_motor_efficiency: float = 0.82
    default_prop_efficiency: float = 0.65
    air_viscosity_pa_s: float = 1.7894e-5
