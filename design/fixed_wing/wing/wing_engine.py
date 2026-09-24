"""
Fixed-Wing Wing Engine Subsystem

Purpose:
    Defines the `WingEngine` class, which serves as the orchestrator for the Wing Engineering Framework.

Role in Architecture:
    `WingEngine` acts as the coordinator, pulling together strategies, sizers, validators,
    and analysis services to calculate the wing dimensions.
"""

import math
from typing import List, Dict, Any
from datetime import datetime

from backend.design.fixed_wing.wing.wing_requirements import WingRequirements, PlanformType
from backend.design.fixed_wing.wing.wing_profile import WingProfile
from backend.design.fixed_wing.wing.wing_constraints import WingConstraints
from backend.design.fixed_wing.wing.wing_geometry import WingGeometry
from backend.design.fixed_wing.wing.wing_analysis import WingAnalysis, WingAnalysisService
from backend.design.fixed_wing.wing.wing_result import WingResult
from backend.design.fixed_wing.wing.wing_validator import WingValidator
from backend.design.fixed_wing.wing.wing_registry import WingStrategyRegistry
from backend.design.fixed_wing.wing.wing_sizer import WingSizer
from backend.design.fixed_wing.wing.wing_planform import PlanformGeometryService


class WingEngine:
    """
    Facade class managing the aircraft wing geometry sizing pipeline.
    """

    def __init__(
        self,
        sizer: WingSizer | None = None,
        planform_service: PlanformGeometryService | None = None,
        analysis_service: WingAnalysisService | None = None,
        validator: WingValidator | None = None,
    ) -> None:
        self._sizer = sizer if sizer else WingSizer()
        self._planform_service = planform_service if planform_service else PlanformGeometryService()
        self._analysis_service = analysis_service if analysis_service else WingAnalysisService()
        self._validator = validator if validator else WingValidator()

    def process_wing_design(
        self,
        requirements: WingRequirements,
        profile: WingProfile | None = None,
    ) -> WingResult:
        """
        Calculates and validates the primary lifting wing dimensions.

        Args:
            requirements (WingRequirements): Mission and layout context with user overrides.
            profile (WingProfile | None): Sizing parameters configuration.

        Returns:
            WingResult: Complete primary wing geometry selection.
        """
        if profile is None:
            profile = WingProfile()

        mission_profile = requirements.mission_result.mission_profile
        category = mission_profile.mission_category

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = WingStrategyRegistry.get(strategy_name)

        # 2. Extract wingspan limit from mission constraints
        max_span = requirements.mission_result.constraints.maximum_takeoff_weight_kg  # wait, this was weight limit
        # Let's check if there is an explicit wingspan limit in metadata or requirements
        max_span_m = requirements.metadata.get("max_wingspan_m")

        # Estimate fuselage width to enforce root chord compatibility
        mission_profile = requirements.mission_result.mission_profile
        payload_mass = mission_profile.payload_kg
        min_payload_width = 0.08 + (payload_mass * 0.005)
        clearance_margin = 0.02
        min_fuse_width = min_payload_width + 2.0 * clearance_margin
        fuse_res = getattr(requirements, "fuselage_result", None)
        if fuse_res and hasattr(fuse_res, "fuselage_geometry"):
            min_fuse_width = max(min_fuse_width, fuse_res.fuselage_geometry.width_m)

        # Aerodynamic and structural clearance margin:
        # Wing root chord must exceed fuselage width to ensure structural carry-through
        # attachment and avoid junction aerodynamic blockage/separation.
        clearance_factor = 1.10
        min_root_chord_m = min_fuse_width * clearance_factor

        # Define wing constraints
        constraints = WingConstraints(
            max_wingspan_m=max_span_m,
            min_aspect_ratio=profile.min_aspect_ratio,
            max_aspect_ratio=profile.max_aspect_ratio,
            min_wing_loading_kg_m2=profile.min_wing_loading_kg_m2,
            max_wing_loading_kg_m2=profile.max_wing_loading_kg_m2,
            min_root_chord_m=min_root_chord_m,
        )

        # 3. Size main parameters S and AR
        target_ar = strategy.get_target_aspect_ratio()
        typical_wl = strategy.get_typical_wing_loading_kg_m2()

        size_data = self._sizer.size_wing(requirements, constraints, target_ar, typical_wl)
        area = size_data["area_m2"]
        ar = size_data["aspect_ratio"]
        span = size_data["span_m"]
        wl = size_data["wing_loading_kg_m2"]
        mtow = size_data["mtow_kg"]

        # 4. Determine angles from strategy
        sweep, dihedral, incidence = strategy.get_sweep_and_dihedral(requirements)
        planform = strategy.get_planform_type(requirements)

        # 5. Size planform distribution (Root/Tip chords, MAC, Quarter-chord location)
        planform_data = self._planform_service.calculate_planform_dimensions(planform, area, ar, sweep)
        root_chord = planform_data["root_chord_m"]

        # Geometric coupling constraint: enforce root chord >= min_root_chord_m for specific planform
        if constraints.min_root_chord_m is not None and root_chord < constraints.min_root_chord_m:
            req_chord = constraints.min_root_chord_m
            if planform in (PlanformType.TAPERED, PlanformType.TRAPEZOIDAL, PlanformType.SWEPT):
                taper = planform_data.get("taper_ratio", 0.5)
                if taper <= 0.0:
                    taper = 0.5
                max_ar = ((2.0 * math.sqrt(area)) / (req_chord * (1.0 + taper))) ** 2
            elif planform == PlanformType.ELLIPTICAL:
                max_ar = ((4.0 * math.sqrt(area)) / (math.pi * req_chord)) ** 2
            else:
                max_ar = (math.sqrt(area) / req_chord) ** 2

            ar = max(constraints.min_aspect_ratio, min(ar, max_ar))
            span = math.sqrt(area * ar)
            planform_data = self._planform_service.calculate_planform_dimensions(planform, area, ar, sweep)
            root_chord = planform_data["root_chord_m"]

        tip_chord = planform_data["tip_chord_m"]
        taper_ratio = planform_data["taper_ratio"]
        mac = planform_data["mean_aerodynamic_chord_m"]
        quarter_chord_x = planform_data["quarter_chord_x_m"]

        # Build WingGeometry object
        geometry = WingGeometry(
            span_m=span,
            area_m2=area,
            aspect_ratio=ar,
            wing_loading_kg_m2=wl,
            root_chord_m=root_chord,
            tip_chord_m=tip_chord,
            taper_ratio=taper_ratio,
            sweep_angle_deg=sweep,
            dihedral_angle_deg=dihedral,
            wing_incidence_deg=incidence,
            mean_aerodynamic_chord_m=mac,
            quarter_chord_x_m=quarter_chord_x,
            reference_area_m2=area,
        )

        # 6. Calculate structural limits
        design_load_factor = 4.0  # Limit load factor
        structural_results = self._sizer._structure.evaluate_structural_feasibility(
            geometry, mtow, design_load_factor
        )

        # 7. Perform detailed performance analysis
        analysis = self._analysis_service.analyze_wing(
            requirements, geometry, mtow, structural_results
        )

        # 8. Validate sized geometry
        warnings = self._validator.validate(requirements, constraints, geometry, structural_results)

        # 9. Extract notes and recommendations
        wing_weight_kg = round(self._sizer._structure.estimate_wing_weight_kg(geometry, design_load_factor), 4)
        mtow_val = round(mtow, 4)

        engineering_notes = [
            f"Wing sizing complete. Aspect Ratio: {ar:.2f}, Wing Area: {area:.4f} m2.",
            f"Estimated MTOW: {mtow_val:.2f} kg, Cruise Lift Coefficient: {analysis.lift_coefficient_cruise:.3f}.",
            f"Estimated Stall Speed: {analysis.estimated_stall_speed_kmh:.1f} km/h.",
            f"Estimated Wing weight: {wing_weight_kg:.3f} kg.",
        ]
        
        recommendations = strategy.get_recommendations(geometry)

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
            "design_load_factor": design_load_factor,
        }

        # 10. Return compiled WingResult
        return WingResult(
            wing_geometry=geometry,
            planform=planform.value if hasattr(planform, 'value') else str(planform),
            reference_area=area,
            aspect_ratio=ar,
            wing_loading=wl,
            mean_aerodynamic_chord=mac,
            quarter_chord_location=quarter_chord_x,
            analysis=analysis,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
            estimated_mtow_kg=mtow_val,
            estimated_wing_weight_kg=wing_weight_kg,
        )
