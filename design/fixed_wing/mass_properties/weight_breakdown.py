"""
Fixed-Wing Weight Breakdown Subsystem

Purpose:
    Defines the `WeightBreakdown` class representing mass fraction ratios.

Role in Architecture:
    `WeightBreakdown` holds total structural, electrical, avionics, payload, and fuel weight fractions.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class WeightBreakdown:
    """
    Subsystem weight breakdown percentages.

    Attributes:
        structural_weight_kg (float): Combined wing + tail + fuselage weight.
        propulsion_weight_kg (float): Motor + propeller weight.
        avionics_weight_kg (float): Autopilot + wire modems weight.
        payload_weight_kg (float): Mission cameras + cargo weight.
        battery_fuel_weight_kg (float): Sized battery/fuel weight.
        useful_load_kg (float): Sized payload + battery load.
        payload_fraction (float): Sized payload ratio (payload / MTOW).
        battery_fraction (float): Sized battery ratio (battery / MTOW).
    """

    structural_weight_kg: float
    propulsion_weight_kg: float
    avionics_weight_kg: float
    payload_weight_kg: float
    battery_fuel_weight_kg: float
    useful_load_kg: float
    payload_fraction: float
    battery_fraction: float
