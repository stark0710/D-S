"""
Fixed-Wing Mass Properties Profile Subsystem

Purpose:
    Defines the `MassProfile` class, which holds safety factor ranges and stability margins targets.

Role in Architecture:
    The profile is used to configure target static margins, neutral point calculations, and inertia margins.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class MassProfile:
    """
    Configuration profile defining limits and stability margins for mass balance.

    Attributes:
        min_static_margin (float): Minimum allowable static stability margin (default 0.05 / 5% MAC).
        max_static_margin (float): Maximum allowable static stability margin (default 0.25 / 25% MAC).
        default_neutral_point_mac_pct (float): Position of neutral point as fraction of Mean Aerodynamic Chord (default 0.35).
        reserve_weight_fraction (float): Safety contingency fraction of empty weight (default 0.05).
    """

    min_static_margin: float = 0.05
    max_static_margin: float = 0.25
    default_neutral_point_mac_pct: float = 0.35
    reserve_weight_fraction: float = 0.05
    battery_specific_energy_wh_kg: float = 200.0
