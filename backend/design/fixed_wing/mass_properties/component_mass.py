"""
Fixed-Wing Component Mass Subsystem

Purpose:
    Defines the `ComponentMass` class representing individual airframe and electronics weights.

Role in Architecture:
    `ComponentMass` holds individual mass records (kg) and their spatial locations (meters from nose).
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ComponentMass:
    """
    Subsystem component mass and coordinate mapping.

    Attributes:
        name (str): Component identifier (e.g. Wing, Battery, Motor).
        mass_kg (float): Weight in kilograms.
        x_m (float): Longitudinal distance from nose in meters.
        y_m (float): Lateral distance from centerline in meters.
        z_m (float): Vertical distance from centerline in meters.
    """

    name: str
    mass_kg: float
    x_m: float
    y_m: float
    z_m: float
