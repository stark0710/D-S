"""
VTOL Tail Sizing Engine Subsystem

Purpose:
    Defines the `TailEngine` facade class orchestrating stabilizer sizing,
    static stability margins, control surface areas, and validation checks.
"""

from typing import List, Dict, Any
import math
from datetime import datetime

from backend.design.vtol.tail.tail_requirements import TailRequirements
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.tail.tail_geometry import TailGeometry
from backend.design.vtol.tail.tail_structure import TailStructure
from backend.design.vtol.tail.tail_controls import TailControls
from backend.design.vtol.tail.tail_analysis import TailStabilityAnalysis, TailControlAnalysis
from backend.design.vtol.tail.tail_validator import TailValidator
from backend.design.vtol.tail.tail_registry import VTOLTailStrategyRegistry
from backend.design.vtol.tail.tail_sizer import TailSizer
from backend.design.vtol.tail.authoritative_stability import AuthoritativeStabilityEngine


class TailEngine:
    """
    Facade orchestrator driving empennage sizing, controls, and stability assessments.
    """

    def __init__(
        self,
        validator: TailValidator | None = None,
        sizer: TailSizer | None = None,
    ) -> None:
        self._validator = validator or TailValidator()
        self._sizer = sizer or TailSizer()

    def size_tail_system(self, requirements: TailRequirements) -> TailResult:
        """
        Orchestrates the complete tail system design pipeline.

        Args:
            requirements (TailRequirements): Sizing inputs.

        Returns:
            TailResult: Complete tail definition.
        """
        mission_res = requirements.mission_result
        config_res = requirements.configuration_result
        wing_res = requirements.wing_result

        # 1. Strategy selection
        strategy = VTOLTailStrategyRegistry.get(mission_res.mission_profile.mission_category)

        # 2. Sizing geometry
        wing_area = wing_res.wing_geometry.area_m2
        wing_span = wing_res.wing_geometry.span_m
        root_chord = wing_res.wing_geometry.root_chord_m
        taper = wing_res.wing_geometry.taper_ratio
        mac = root_chord * (2.0 / 3.0) * ((1.0 + taper + taper**2) / (1.0 + taper))

        tail_config = requirements.preferred_tail_configuration
        if not tail_config and config_res and hasattr(config_res, "vtol_configuration") and config_res.vtol_configuration:
            tail_config = getattr(config_res.vtol_configuration, "tail_configuration", None)
        if not tail_config:
            tail_config = strategy.default_tail_configuration

        sized = self._sizer.size_tail(
            wing_area=wing_area,
            wing_span=wing_span,
            mac=mac,
            target_vh=strategy.default_vh,
            target_vv=strategy.default_vv,
            tail_config=tail_config,
        )

        geom = TailGeometry(
            tail_configuration=tail_config,
            tail_arm_m=sized["tail_arm_m"],
            horizontal_area_m2=sized["horizontal_area_m2"],
            horizontal_span_m=sized["horizontal_span_m"],
            horizontal_aspect_ratio=sized["horizontal_aspect_ratio"],
            vertical_area_m2=sized["vertical_area_m2"],
            vertical_span_m=sized["vertical_span_m"],
            vertical_aspect_ratio=sized["vertical_aspect_ratio"],
            v_tail_angle_deg=sized["v_tail_angle_deg"],
        )

        # 3. Flap / Control surface sizing
        # Elevator flap is typically 25% horizontal stabilizer area
        elev_area = sized["horizontal_area_m2"] * 0.25
        # Rudder flap is typically 30% vertical stabilizer area
        rudder_area = sized["vertical_area_m2"] * 0.30

        controls = TailControls(
            elevator_area_m2=round(elev_area, 4),
            elevator_span_m=sized["horizontal_span_m"],
            rudder_area_m2=round(rudder_area, 4),
            rudder_span_m=sized["vertical_span_m"],
            control_mixing_type=strategy.control_mixing_type,
        )

        # 4. Structure & Weight sizing
        mtow = mission_res.mission_analysis.estimated_mtow_kg
        scale = max(0.6, min(2.5, (mtow / 10.0) ** 0.33))

        total_stab_area = sized["horizontal_area_m2"] + sized["vertical_area_m2"]
        # Empirical tail weight (mass of stabilizers + boom mount connectors)
        tail_weight = total_stab_area * 1.95 * scale

        if tail_config == "Twin Boom Tail":
            concept = "Carbon fiber sandwich on twin boom sleeves"
            boom_diam = max(16.0, min(45.0, mtow * 1.1))
            boom_mat = "High-modulus carbon tubes"
        elif tail_config in ("Tailless", "Tail Sitter"):
            concept = "None - Integrated elevon surfaces"
            boom_diam = 0.0
            boom_mat = "None"
            tail_weight = 0.0
        else:
            concept = "Molded composite fuselage fin joint"
            boom_diam = 0.0
            boom_mat = "None"

        struct = TailStructure(
            structural_concept=concept,
            estimated_tail_weight_kg=round(tail_weight, 3),
            boom_diameter_mm=round(boom_diam, 1),
            boom_material=boom_mat,
        )

        # 5. Stability & Control Analysis
        # Static margin: X_np - X_cg. For conventional, typically 10-20% MAC
        has_stabilizer = sized["horizontal_area_m2"] > 0
        static_margin = 15.0 if has_stabilizer else 4.0  # tailless has low static margin
        neutral_point = 40.0 if has_stabilizer else 25.0

        long_score = 90.0 if tail_config == "Conventional Tail" else (80.0 if has_stabilizer else 30.0)
        dir_score = 88.0 if sized["vertical_area_m2"] > 0 else 25.0

        stab_anal = TailStabilityAnalysis(
            longitudinal_stability_score=long_score,
            directional_stability_score=dir_score,
            static_margin_percent=static_margin,
            neutral_point_percent=neutral_point,
            trim_capability_deg=2.5,
        )

        # Slipstream/wash parameters
        is_pusher = "Pusher" in config_res.lift_architecture.forward_propulsion_layout
        slipstream_factor = 1.25 if is_pusher else 1.0
        downwash_index = 0.35 if has_stabilizer else 0.0

        control_anal = TailControlAnalysis(
            pitch_effectiveness=75.0 if has_stabilizer else 20.0,
            yaw_effectiveness=75.0 if sized["vertical_area_m2"] > 0 else 15.0,
            transition_authority=80.0 if has_stabilizer else 35.0,
            rotor_downwash_interference_index=downwash_index,
            slipstream_influence_factor=slipstream_factor,
            hover_mode_control_authority=15.0 if tail_config == "Tail Sitter" else 0.0,
        )

        # 6. Warnings, Notes, Recommendations
        notes = [
            f"Empennage configuration selected: {tail_config}.",
            f"Horizontal stabilizer area sized: {geom.horizontal_area_m2:.4f} m².",
            f"Vertical stabilizer area sized: {geom.vertical_area_m2:.4f} m².",
        ]

        recs = strategy.get_recommendations()
        warnings: List[str] = []

        if tail_config == "Conventional Tail" and wing_res.wing_geometry.wing_position == "High Wing":
            recs.append("Assess downwash wake from high wing during wing-stall transitions to avoid horizontal tail buffeting.")
        if tail_config == "Tailless":
            warnings.append("Tailless configuration has limited pitch static margin. Ensure strict CG loading constraints.")

        # 7. Assemble result package
        result = TailResult(
            tail_geometry=geom,
            tail_structure=struct,
            control_surfaces=controls,
            stability_analysis=stab_anal,
            control_analysis=control_anal,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
        )

        # Preliminary Authoritative Stability & Control sizing (Phase 6)
        wing_pos = getattr(wing_res, "wing_position", None)
        root_le_x = getattr(wing_pos, "root_le_x_m", 0.440) if wing_pos else 0.440
        est_cg_x = root_le_x + 0.303 * mac
        try:
            auth_res = AuthoritativeStabilityEngine.analyze_stability_and_control(
                converged_mtow_kg=mtow,
                converged_cg_x_m=est_cg_x,
                wing_result=wing_res,
                tail_result=result,
                airfoil_result=getattr(requirements, "airfoil_result", None),
            )
            result.authoritative_stability_result = auth_res
        except Exception:
            pass

        # 8. Validate results
        self._validator.validate(requirements, result)

        # Metadata
        meta = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.__class__.__name__,
        }
        result.metadata = meta

        return result
