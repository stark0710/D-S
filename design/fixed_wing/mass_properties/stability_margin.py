"""
Fixed-Wing Static Stability Margin Subsystem

Purpose:
    Defines the `StabilityMarginCalculator` class.

Role in Architecture:
    `StabilityMarginCalculator` calculates neutral point positions and static margins.
"""

from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.tail.tail_result import TailResult


class StabilityMarginCalculator:
    """
    Sizing service resolving longitudinal static margins.
    """

    def calculate_static_margin(
        self,
        cg_x: float,
        wing_geom: WingGeometry,
        tail_result: TailResult | None = None,
        neutral_point_override_pct: float | None = None,
        wing_attachment_x_m: float | None = None,
    ) -> float:
        """
        Computes static margin as a fraction of wing MAC.

        Static Margin = (X_np - X_cg) / MAC
        """
        mac = wing_geom.mean_aerodynamic_chord_m
        quarter_chord_x = wing_geom.quarter_chord_x_m
        wing_x = wing_attachment_x_m if wing_attachment_x_m is not None else 0.0

        # Estimate neutral point (usually 35% to 45% of MAC for Conventional,
        # or 25% for Flying Wings)
        np_pct = neutral_point_override_pct if neutral_point_override_pct else 0.38
        
        if tail_result and tail_result.tail_configuration == "Conventional":
            np_pct = 0.42  # horizontal tail shifts neutral point aft
        elif tail_result and tail_result.tail_configuration == "Tailless":
            np_pct = 0.25  # tailless has no aft tail to stabilize pitch

        if wing_x > 0.0 or cg_x > (quarter_chord_x + mac):
            global_quarter_chord = wing_x + quarter_chord_x
            neutral_point_x = global_quarter_chord + (np_pct * mac)
        else:
            neutral_point_x = quarter_chord_x + (np_pct * mac)

        static_margin = (neutral_point_x - cg_x) / max(0.01, mac)
        return static_margin
