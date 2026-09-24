"""
VTOL Wing Sizer Subsystem

Purpose:
    Defines the `WingSizer` utility class solving aerodynamic planform formulas
    and structural mass scaling equations.
"""

import math
from typing import Dict, Any


class WingSizer:
    """
    Sizing utility to solve wing planform areas, spans, chords, and weight estimates.
    """

    def size_wing(
        self,
        mtow_kg: float,
        target_loading: float,
        target_ar: float,
        taper_ratio: float,
        override_span: float | None = None,
        override_ar: float | None = None,
    ) -> Dict[str, Any]:
        """
        Sizes a wing geometry and structural weight based on target constraints.

        Args:
            mtow_kg (float): Sized Maximum Takeoff Weight.
            target_loading (float): Sized wing loading (kg/m²).
            target_ar (float): Target aspect ratio.
            taper_ratio (float): Target taper ratio.
            override_span (float | None): Preferred wing span override.
            override_ar (float | None): Preferred aspect ratio override.

        Returns:
            Dict[str, Any]: Sized wing dimensions and mass.
        """
        # 1. Solve planform area
        area_m2 = mtow_kg / target_loading

        # Apply aspect ratio / span overrides
        if override_span is not None:
            span_m = override_span
            aspect_ratio = (span_m ** 2) / area_m2
        elif override_ar is not None:
            aspect_ratio = override_ar
            span_m = math.sqrt(area_m2 * aspect_ratio)
        else:
            aspect_ratio = target_ar
            span_m = math.sqrt(area_m2 * aspect_ratio)

        # 2. Solve chords
        # S = 0.5 * (c_root + c_tip) * b = 0.5 * c_root * (1 + taper) * b
        root_chord = (2.0 * area_m2) / (span_m * (1.0 + taper_ratio))
        tip_chord = root_chord * taper_ratio

        # 3. Solve structural weight
        # Empirical fixed-wing composite weight scaling with area and aspect ratio
        wing_weight_kg = area_m2 * 2.25 * (1.0 + (aspect_ratio - 8.0) * 0.07)

        return {
            "area_m2": round(area_m2, 4),
            "span_m": round(span_m, 3),
            "aspect_ratio": round(aspect_ratio, 2),
            "root_chord_m": round(root_chord, 3),
            "tip_chord_m": round(tip_chord, 3),
            "wing_weight_kg": round(wing_weight_kg, 3),
        }
