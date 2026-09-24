"""
Fixed-Wing Wing Planform Geometry Subsystem

Purpose:
    Defines the `PlanformGeometryService` class to calculate chords, MAC, and quarter-chord points.

Role in Architecture:
    `PlanformGeometryService` implements physics-based planform calculations for Rectangular,
    Tapered, Trapezoidal, Elliptical, Swept, Delta, Cranked, and Custom wings.
"""

import math
from typing import Dict, Any
from backend.design.fixed_wing.wing.wing_requirements import PlanformType


class PlanformGeometryService:
    """
    Engineering utility to calculate planform dimensions based on wing area and aspect ratio.
    """

    def calculate_planform_dimensions(
        self,
        planform: PlanformType,
        area_m2: float,
        aspect_ratio: float,
        sweep_angle_deg: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculates span, root chord, tip chord, taper ratio, MAC, and quarter-chord point.

        Args:
            planform (PlanformType): Planform style.
            area_m2 (float): Reference planform area.
            aspect_ratio (float): Wing aspect ratio.
            sweep_angle_deg (float): Leading edge sweep in degrees.

        Returns:
            Dict[str, float]: Geometry values.
        """
        # Wingspan: b = sqrt(S * AR)
        span = math.sqrt(area_m2 * aspect_ratio)
        sweep_rad = math.radians(sweep_angle_deg)

        # Standard planform heuristics
        if planform == PlanformType.RECTANGULAR:
            taper_ratio = 1.0
            root_chord = area_m2 / span
            tip_chord = root_chord
            mac = root_chord
            # For rectangular wing with no sweep, quarter chord is at 25% root chord
            quarter_chord_x = 0.25 * root_chord

        elif planform in (PlanformType.TAPERED, PlanformType.TRAPEZOIDAL, PlanformType.SWEPT):
            # Standard tapered wing has a taper ratio between 0.4 and 0.7 for induced drag optimization
            taper_ratio = 0.5
            if planform == PlanformType.SWEPT and sweep_angle_deg == 0.0:
                sweep_angle_deg = 20.0  # default sweep
                sweep_rad = math.radians(sweep_angle_deg)

            root_chord = (2.0 * area_m2) / (span * (1.0 + taper_ratio))
            tip_chord = taper_ratio * root_chord

            # MAC calculation for linear taper:
            # MAC = 2/3 * root_chord * (1 + lambda + lambda^2) / (1 + lambda)
            mac = (2.0 / 3.0) * root_chord * (1.0 + taper_ratio + taper_ratio**2) / (1.0 + taper_ratio)

            # Quarter chord position:
            # x_q = 0.25 * MAC + y_mac * tan(sweep_LE)
            # where y_mac is the lateral position of the MAC:
            # y_mac = b/6 * (1 + 2*lambda) / (1 + lambda)
            y_mac = (span / 6.0) * (1.0 + 2.0 * taper_ratio) / (1.0 + taper_ratio)
            quarter_chord_x = 0.25 * mac + y_mac * math.tan(sweep_rad)

        elif planform == PlanformType.ELLIPTICAL:
            # Elliptical wing has taper ratio mathematically leading to 0 at tip
            taper_ratio = 0.0
            root_chord = (4.0 * area_m2) / (math.pi * span)
            tip_chord = 0.0
            # MAC for elliptical wing is 8 / (3 * pi) * root_chord
            mac = (8.0 * area_m2) / (3.0 * math.pi * span)
            quarter_chord_x = 0.25 * root_chord

        elif planform == PlanformType.DELTA:
            taper_ratio = 0.05
            if sweep_angle_deg == 0.0:
                sweep_angle_deg = 45.0  # standard delta sweep
                sweep_rad = math.radians(sweep_angle_deg)

            root_chord = (2.0 * area_m2) / (span * (1.0 + taper_ratio))
            tip_chord = taper_ratio * root_chord
            mac = (2.0 / 3.0) * root_chord * (1.0 + taper_ratio + taper_ratio**2) / (1.0 + taper_ratio)

            # Lateral position of MAC
            y_mac = (span / 6.0) * (1.0 + 2.0 * taper_ratio) / (1.0 + taper_ratio)
            quarter_chord_x = 0.25 * mac + y_mac * math.tan(sweep_rad)

        elif planform in (PlanformType.CRANKED, PlanformType.CUSTOM):
            # Complex/cranked wing: approximate with an averaged tapered formulation
            taper_ratio = 0.4
            root_chord = (2.0 * area_m2) / (span * (1.0 + taper_ratio))
            tip_chord = taper_ratio * root_chord
            mac = (2.0 / 3.0) * root_chord * (1.0 + taper_ratio + taper_ratio**2) / (1.0 + taper_ratio)
            y_mac = (span / 6.0) * (1.0 + 2.0 * taper_ratio) / (1.0 + taper_ratio)
            quarter_chord_x = 0.25 * mac + y_mac * math.tan(sweep_rad)

        else:
            raise ValueError(f"Unsupported planform type: {planform}")

        return {
            "span_m": round(span, 4),
            "root_chord_m": round(root_chord, 4),
            "tip_chord_m": round(tip_chord, 4),
            "taper_ratio": round(taper_ratio, 4),
            "mean_aerodynamic_chord_m": round(mac, 4),
            "quarter_chord_x_m": round(quarter_chord_x, 4),
        }
