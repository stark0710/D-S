"""
Fixed-Wing Tail Engine Subsystem

Purpose:
    Defines the `TailEngine` class, which serves as the orchestrator for the Tail Engineering Framework.

Role in Architecture:
    `TailEngine` coordinates the tail style matching, stabilizer sizing, control surface geometry calculations,
    stability analysis, and validation rules.
"""

from typing import List, Dict, Any
from datetime import datetime

from backend.design.fixed_wing.tail.tail_requirements import TailRequirements, TailConfigType
from backend.design.fixed_wing.tail.tail_profile import TailProfile
from backend.design.fixed_wing.tail.tail_constraints import TailConstraints
from backend.design.fixed_wing.tail.tail_result import TailResult
from backend.design.fixed_wing.tail.tail_validator import TailValidator
from backend.design.fixed_wing.tail.tail_registry import TailStrategyRegistry
from backend.design.fixed_wing.tail.tail_sizer import TailSizer
from backend.design.fixed_wing.tail.tail_analysis import TailAnalysisService, TailAnalysis
from backend.design.fixed_wing.tail.horizontal_tail import HorizontalTail
from backend.design.fixed_wing.tail.vertical_tail import VerticalTail
from backend.design.fixed_wing.tail.control_surface import ControlSurfaces


class TailEngine:
    """
    Facade class managing the aircraft tail and control surface sizing pipeline.
    """

    def __init__(
        self,
        sizer: TailSizer | None = None,
        analysis_service: TailAnalysisService | None = None,
        validator: TailValidator | None = None,
    ) -> None:
        self._sizer = sizer if sizer else TailSizer()
        self._analysis_service = analysis_service if analysis_service else TailAnalysisService()
        self._validator = validator if validator else TailValidator()

    def process_tail_design(
        self,
        requirements: TailRequirements,
        profile: TailProfile | None = None,
    ) -> TailResult:
        """
        Sizes and validates the horizontal, vertical, and control surfaces.

        Args:
            requirements (TailRequirements): Sizing requirements context.
            profile (TailProfile | None): Safety configurations.

        Returns:
            TailResult: Sized tail layout and analysis.
        """
        if profile is None:
            profile = TailProfile()

        m_profile = requirements.mission_result.mission_profile
        wing_geom = requirements.wing_result.wing_geometry
        airfoil_data = requirements.airfoil_result.polar_data
        category = m_profile.mission_category

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = TailStrategyRegistry.get(strategy_name)

        # 2. Define Tail Constraints
        constraints = TailConstraints(
            allowed_styles=[TailConfigType.CONVENTIONAL, TailConfigType.V_TAIL, TailConfigType.TWIN_BOOM],
            min_v_h=profile.min_v_h,
            max_v_h=profile.max_v_h,
            min_v_v=profile.min_v_v,
            max_v_v=profile.max_v_v,
        )

        # 3. Select Tail Style using strategy
        tail_style = strategy.select_tail_style(requirements)

        # 4. Sizing the tail arm l_t
        tail_arm = self._sizer.size_tail_arm(
            wing_geom.span_m, tail_style, profile.default_tail_arm_ratio
        )

        # 5. Sizing horizontal and vertical stabilizer areas
        target_v_h, target_v_v = strategy.get_target_volume_coefficients()
        horiz_area, vert_area = self._sizer.size_stabilizer_areas(
            wing_area_m2=wing_geom.area_m2,
            mac_m=wing_geom.mean_aerodynamic_chord_m,
            span_m=wing_geom.span_m,
            tail_arm_m=tail_arm,
            target_v_h=target_v_h,
            target_v_v=target_v_v,
            tail_style=tail_style,
        )

        # 6. Sizing horizontal and vertical geometries
        horiz_ar, vert_ar = strategy.get_typical_aspect_ratios()
        h_sweep, h_taper, v_sweep, v_taper = strategy.get_sweep_and_taper()

        h_tail, v_tail = self._sizer.generate_geometry(
            horizontal_area=horiz_area,
            vertical_area=vert_area,
            horiz_ar=horiz_ar,
            vert_ar=vert_ar,
            horiz_sweep=h_sweep,
            horiz_taper=h_taper,
            vert_sweep=v_sweep,
            vert_taper=v_taper,
            tail_style=tail_style,
        )

        # 7. Sizing control surfaces (elevator and rudder chord ratios)
        elevator_ratio, rudder_ratio = strategy.get_control_surface_ratios()
        control_surfaces = self._sizer.size_control_surfaces(
            h_tail=h_tail,
            v_tail=v_tail,
            elevator_ratio=elevator_ratio,
            rudder_ratio=rudder_ratio,
            tail_style=tail_style,
        )

        # 8. Detailed performance and stability analysis
        analysis = self._analysis_service.analyze_tail_performance(
            wing_area_m2=wing_geom.area_m2,
            mac_m=wing_geom.mean_aerodynamic_chord_m,
            span_m=wing_geom.span_m,
            horizontal_area_m2=h_tail.area_m2,
            vertical_area_m2=v_tail.area_m2,
            tail_arm_m=tail_arm,
            tail_style=tail_style.value,
            elevator_chord_ratio=elevator_ratio,
            rudder_chord_ratio=rudder_ratio,
            c_m0=airfoil_data.pitching_moment_c_m0,
        )

        # 9. Validate sized geometry
        warnings = self._validator.validate(
            requirements, constraints, tail_style, h_tail, v_tail, control_surfaces, analysis
        )

        # 10. Compile notes and recommendations
        engineering_notes = [
            f"Tail configuration: {tail_style.value}.",
            f"Tail arm: {tail_arm:.2f} m.",
            f"Sized horizontal tail area: {h_tail.area_m2:.4f} m2, V_h = {analysis.horizontal_volume_coefficient:.3f}.",
            f"Sized vertical tail area: {v_tail.area_m2:.4f} m2, V_v = {analysis.vertical_volume_coefficient:.3f}.",
        ]
        
        recommendations = strategy.get_recommendations(analysis)

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
        }

        # 11. Return compiled TailResult
        return TailResult(
            tail_configuration=tail_style.value,
            horizontal_tail=h_tail,
            vertical_tail=v_tail,
            control_surfaces=control_surfaces,
            tail_volume_coefficients={
                "horizontal_V_h": analysis.horizontal_volume_coefficient,
                "vertical_V_v": analysis.vertical_volume_coefficient,
            },
            tail_analysis=analysis,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
