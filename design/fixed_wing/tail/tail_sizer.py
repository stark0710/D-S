"""
Fixed-Wing Tail Sizer Subsystem

Purpose:
    Defines the `TailSizer` class, which handles horizontal, vertical, and control surface sizing equations.

Role in Architecture:
    `TailSizer` computes stabilizer areas, sweeps, chords, spans, and elevator/rudder dimensions.
"""

import math
from typing import Dict, Any, Tuple
from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.control_surface import ControlSurfaces


class TailSizer:
    """
    Sizing service responsible for solving empennage and control surface equations.
    """

    def size_tail_arm(self, span_m: float, tail_style: TailConfigType, default_ratio: float) -> float:
        """Estimates the longitudinal tail arm length."""
        if tail_style in (TailConfigType.TAILLESS, TailConfigType.FLYING_WING):
            return 0.0
        # Typical small UAV tail arm is 50-65% of wingspan
        return round(default_ratio * span_m, 3)

    def size_stabilizer_areas(
        self,
        wing_area_m2: float,
        mac_m: float,
        span_m: float,
        tail_arm_m: float,
        target_v_h: float,
        target_v_v: float,
        tail_style: TailConfigType,
    ) -> Tuple[float, float]:
        """
        Sizes horizontal and vertical tail reference areas based on target volume coefficients.
        """
        if tail_style in (TailConfigType.TAILLESS, TailConfigType.FLYING_WING) or tail_arm_m == 0.0:
            return 0.0, 0.0

        # Horizontal Tail Area: S_h = (V_h * S * c_mac) / l_t
        horizontal_area = (target_v_h * wing_area_m2 * mac_m) / tail_arm_m

        # Vertical Tail Area: S_v = (V_v * S * b) / l_t
        vertical_area = (target_v_v * wing_area_m2 * span_m) / tail_arm_m

        # If it is a V-Tail, the horizontal and vertical area requirements are combined
        # into a single V-Tail project area. For simplicity, we size them individually
        # to represent horizontal and vertical projections.
        return round(horizontal_area, 4), round(vertical_area, 4)

    def generate_geometry(
        self,
        horizontal_area: float,
        vertical_area: float,
        horiz_ar: float,
        vert_ar: float,
        horiz_sweep: float,
        horiz_taper: float,
        vert_sweep: float,
        vert_taper: float,
        tail_style: TailConfigType,
    ) -> Tuple[HorizontalTail, VerticalTail]:
        """
        Calculates spans, chords, and taper ratios for stabilizers.
        """
        # Horizontal
        if horizontal_area > 0.0:
            h_span = math.sqrt(horizontal_area * horiz_ar)
            h_root = (2.0 * horizontal_area) / (h_span * (1.0 + horiz_taper))
            h_tip = horiz_taper * h_root
            h_incidence = 0.0 if tail_style != TailConfigType.CANARD else 3.0
            
            h_tail = HorizontalTail(
                area_m2=round(horizontal_area, 4),
                span_m=round(h_span, 3),
                chord_root_m=round(h_root, 3),
                chord_tip_m=round(h_tip, 3),
                aspect_ratio=horiz_ar,
                sweep_angle_deg=horiz_sweep,
                taper_ratio=horiz_taper,
                incidence_angle_deg=h_incidence,
            )
        else:
            h_tail = HorizontalTail(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Vertical
        if vertical_area > 0.0:
            v_height = math.sqrt(vertical_area * vert_ar)
            v_root = (2.0 * vertical_area) / (v_height * (1.0 + vert_taper))
            v_tip = vert_taper * v_root
            
            v_tail = VerticalTail(
                area_m2=round(vertical_area, 4),
                height_m=round(v_height, 3),
                chord_root_m=round(v_root, 3),
                chord_tip_m=round(v_tip, 3),
                aspect_ratio=vert_ar,
                sweep_angle_deg=vert_sweep,
                taper_ratio=vert_taper,
            )
        else:
            v_tail = VerticalTail(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        return h_tail, v_tail

    def size_control_surfaces(
        self,
        h_tail: HorizontalTail,
        v_tail: VerticalTail,
        elevator_ratio: float,
        rudder_ratio: float,
        tail_style: TailConfigType,
    ) -> ControlSurfaces:
        """
        Sizes elevator and rudder dimensions.
        """
        # Elevator
        if h_tail.area_m2 > 0.0:
            elevator_span = h_tail.span_m
            elevator_area = h_tail.area_m2 * elevator_ratio
            elevator_max_def = 25.0
            elevator_hinge = 1.0 - elevator_ratio
        else:
            elevator_span = 0.0
            elevator_area = 0.0
            elevator_max_def = 0.0
            elevator_hinge = 0.0

        # Rudder
        if v_tail.area_m2 > 0.0:
            rudder_height = v_tail.height_m
            rudder_area = v_tail.area_m2 * rudder_ratio
            rudder_max_def = 30.0
            rudder_hinge = 1.0 - rudder_ratio
        else:
            rudder_height = 0.0
            rudder_area = 0.0
            rudder_max_def = 0.0
            rudder_hinge = 0.0

        # If tailless or flying wing, pitch/yaw is handled by elevons/winglet rudders
        if tail_style in (TailConfigType.TAILLESS, TailConfigType.FLYING_WING):
            # mock standard values to represent elevons
            elevator_span = 0.0
            elevator_area = 0.0
            elevator_max_def = 0.0
            elevator_hinge = 0.0

        return ControlSurfaces(
            elevator_span_m=round(elevator_span, 3),
            elevator_chord_ratio=round(elevator_ratio, 3),
            elevator_area_m2=round(elevator_area, 4),
            elevator_max_deflection_deg=elevator_max_def,
            elevator_hinge_location_pct=round(elevator_hinge * 100.0, 1),
            
            rudder_height_m=round(rudder_height, 3),
            rudder_chord_ratio=round(rudder_ratio, 3),
            rudder_area_m2=round(rudder_area, 4),
            rudder_max_deflection_deg=rudder_max_def,
            rudder_hinge_location_pct=round(rudder_hinge * 100.0, 1),
        )
