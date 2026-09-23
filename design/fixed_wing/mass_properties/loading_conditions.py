"""
Fixed-Wing Loading Conditions Subsystem

Purpose:
    Defines the `LoadingCondition` class representing different payload/battery layouts.

Role in Architecture:
    `LoadingCondition` holds coordinate and mass properties for flight envelopes (Empty, MTOW, etc).
"""

from dataclasses import dataclass


@dataclass(slots=True)
class LoadingCondition:
    """
    Flight envelope loading state description.

    Attributes:
        condition_name (str): Name (e.g. Empty, Maximum Payload, Mission Start).
        total_mass_kg (float): Sized total mass.
        cg_x_m (float): Longitudinal CG location.
        cg_y_m (float): Lateral CG location.
        cg_z_m (float): Vertical CG location.
        static_margin_pct (float): Sized stability margin.
    """

    condition_name: str
    total_mass_kg: float
    cg_x_m: float
    cg_y_m: float
    cg_z_m: float
    static_margin_pct: float
