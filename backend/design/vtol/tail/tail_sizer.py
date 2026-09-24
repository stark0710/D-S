"""
VTOL Tail Sizer Subsystem

Purpose:
    Defines the `TailSizer` utility class solving empennage stabilizer areas,
    span widths, and dihedral angles.
"""

import math
from typing import Dict, Any


class TailSizer:
    """
    Sizing utility to solve horizontal, vertical, and V-tail geometry matrices.
    """

    def size_tail(
        self,
        wing_area: float,
        wing_span: float,
        mac: float,
        target_vh: float,
        target_vv: float,
        tail_config: str,
    ) -> Dict[str, Any]:
        """
        Sizes tail surfaces and arm lengths based on volume coefficients.
        """
        # If tailless or tail-sitter, stabilizer surfaces are structurally zero
        if tail_config in ("Tailless", "Tail Sitter"):
            return {
                "tail_arm_m": 0.0,
                "horizontal_area_m2": 0.0,
                "horizontal_span_m": 0.0,
                "horizontal_aspect_ratio": 0.0,
                "vertical_area_m2": 0.0,
                "vertical_span_m": 0.0,
                "vertical_aspect_ratio": 0.0,
                "v_tail_angle_deg": 0.0,
            }

        # 1. Tail arm length (distance from wing AC to tail AC)
        tail_arm_m = 2.45 * mac

        # 2. Horizontal tail area
        # Vh = Sh * L / (S * MAC) -> Sh = Vh * S * MAC / L
        horizontal_area = (target_vh * wing_area * mac) / tail_arm_m

        # Horizontal span and chord
        ar_h = 3.5
        horizontal_span = math.sqrt(horizontal_area * ar_h)

        # 3. Vertical tail area
        # Vv = Sv * L / (S * b) -> Sv = Vv * S * b / L
        vertical_area = (target_vv * wing_area * wing_span) / tail_arm_m

        # Vertical fin height and chord
        ar_v = 1.6
        vertical_span = math.sqrt(vertical_area * ar_v)

        # 4. If V-Tail, combine horizontal & vertical
        v_tail_angle = 0.0
        if "v-tail" in tail_config.lower():
            # Projected area methods: dihedral angle theta = arctan(sqrt(Sv / Sh))
            v_tail_angle = math.degrees(math.atan2(math.sqrt(vertical_area), math.sqrt(horizontal_area)))
            # Total area of V-tail panels is Sh + Sv
            # Horizontal & vertical projected areas are maintained
            pass

        return {
            "tail_arm_m": round(tail_arm_m, 3),
            "horizontal_area_m2": round(horizontal_area, 4),
            "horizontal_span_m": round(horizontal_span, 3),
            "horizontal_aspect_ratio": ar_h,
            "vertical_area_m2": round(vertical_area, 4),
            "vertical_span_m": round(vertical_span, 3),
            "vertical_aspect_ratio": ar_v,
            "v_tail_angle_deg": round(v_tail_angle, 1),
        }
