"""
Fixed-Wing Airfoil Engine Subsystem

Purpose:
    Defines the `AirfoilEngine` class, which serves as the orchestrator for the Airfoil Engineering Framework.

Role in Architecture:
    `AirfoilEngine` coordinates the database queries, Reynolds calculations, polar lookups,
    performance grids, and validation rules to select and evaluate wing airfoils.
"""

from typing import List, Dict, Any
from datetime import datetime

from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements
from backend.design.fixed_wing.airfoil.airfoil_profile import AirfoilProfile
from backend.design.fixed_wing.airfoil.airfoil_constraints import AirfoilConstraints
from backend.design.fixed_wing.airfoil.airfoil_result import AirfoilResult
from backend.design.fixed_wing.airfoil.airfoil_validator import AirfoilValidator, AirfoilValidationError
from backend.design.fixed_wing.airfoil.airfoil_registry import AirfoilStrategyRegistry
from backend.design.fixed_wing.airfoil.airfoil_selector import AirfoilSelector
from backend.design.fixed_wing.airfoil.reynolds_analysis import ReynoldsAnalysisService, ReynoldsAnalysis
from backend.design.fixed_wing.airfoil.polar_analysis import PolarAnalysisService, PolarData
from backend.design.fixed_wing.airfoil.performance_map import PerformanceMapService, PerformanceMap
from backend.design.fixed_wing.airfoil.airfoil_analysis import AirfoilAnalysisService, AirfoilAnalysis


class AirfoilEngine:
    """
    Facade class managing the airfoil selection, analysis, and validation pipeline.
    """

    def __init__(
        self,
        reynolds_service: ReynoldsAnalysisService | None = None,
        selector: AirfoilSelector | None = None,
        polar_service: PolarAnalysisService | None = None,
        map_service: PerformanceMapService | None = None,
        analysis_service: AirfoilAnalysisService | None = None,
        validator: AirfoilValidator | None = None,
    ) -> None:
        self._reynolds_service = reynolds_service if reynolds_service else ReynoldsAnalysisService()
        self._selector = selector if selector else AirfoilSelector()
        self._polar_service = polar_service if polar_service else PolarAnalysisService()
        self._map_service = map_service if map_service else PerformanceMapService()
        self._analysis_service = analysis_service if analysis_service else AirfoilAnalysisService()
        self._validator = validator if validator else AirfoilValidator()

    def process_airfoil_design(
        self,
        requirements: AirfoilRequirements,
        profile: AirfoilProfile | None = None,
    ) -> AirfoilResult:
        """
        Selects, analyzes, and validates airfoils for the aircraft wing.

        Args:
            requirements (AirfoilRequirements): Preceding stages results and user settings.
            profile (AirfoilProfile | None): Safety configurations.

        Returns:
            AirfoilResult: Sized airfoil data.
        """
        if profile is None:
            profile = AirfoilProfile()

        m_profile = requirements.mission_result.mission_profile
        wing_geom = requirements.wing_result.wing_geometry
        category = m_profile.mission_category

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = AirfoilStrategyRegistry.get(strategy_name)

        # 2. Estimate Reynolds numbers across span
        air_density = m_profile.air_density_kg_m3
        cruise_speed_m_s = m_profile.cruise_speed_kmh / 3.6
        
        # Sized stall speed from wing result analysis if available, otherwise fallback
        stall_speed_m_s = (requirements.wing_result.analysis.estimated_stall_speed_kmh / 3.6)
        
        reynolds_data: ReynoldsAnalysis = self._reynolds_service.analyze_reynolds_envelope(
            air_density=air_density,
            cruise_speed_m_s=cruise_speed_m_s,
            stall_speed_m_s=stall_speed_m_s,
            root_chord_m=wing_geom.root_chord_m,
            tip_chord_m=wing_geom.tip_chord_m,
            mac_m=wing_geom.mean_aerodynamic_chord_m,
        )

        # 3. Select optimal airfoils based on strategy recommendations
        root_airfoil_primary, tip_airfoil_primary, distribution = self._selector.select_airfoils(requirements, strategy)

        # 4. Define Airfoil Constraints
        constraints = AirfoilConstraints(
            allowed_types=strategy.get_allowed_types(),
            max_pitching_moment_magnitude=profile.max_absolute_c_m,
            min_thickness_to_chord=profile.min_thickness_ratio,
        )

        root_candidates = [root_airfoil_primary]
        alts = self._selector.find_alternatives(root_airfoil_primary, constraints.allowed_types)
        root_candidates.extend(alts)

        last_exception = None
        root_airfoil = root_airfoil_primary
        tip_airfoil = tip_airfoil_primary
        polar_root = None
        polar_tip = None
        performance_map = None
        analysis = None
        warnings = []

        for candidate_root in root_candidates:
            try:
                root_airfoil = candidate_root
                tip_airfoil = tip_airfoil_primary
                
                # 5. Run Polar Analyses at relevant Reynolds numbers
                # Cruise Cl at root
                target_cl = requirements.wing_result.analysis.lift_coefficient_cruise
                polar_root = self._polar_service.analyze_polar(
                    root_airfoil, target_cl, reynolds_data.re_root_cruise
                )
                polar_tip = self._polar_service.analyze_polar(
                    tip_airfoil, target_cl, reynolds_data.re_tip_cruise if reynolds_data.re_tip_cruise > 0 else reynolds_data.re_root_cruise
                )

                # 6. Generate 2D performance maps
                performance_map = self._map_service.generate_map(
                    root_airfoil,
                    reynolds_min=reynolds_data.re_root_stall,
                    reynolds_max=reynolds_data.re_root_cruise,
                )

                # 7. Detailed performance analysis
                analysis = self._analysis_service.analyze_airfoil_performance(
                    root_airfoil, polar_root, polar_tip, reynolds_data
                )

                # 8. Validate airfoil selection
                warnings = self._validator.validate(
                    requirements, constraints, root_airfoil, tip_airfoil, reynolds_data
                )
                break
            except AirfoilValidationError as e:
                last_exception = e
                continue
        else:
            raise AirfoilValidationError([
                f"AIRFOIL_STRUCTURE_INCOMPATIBLE: No compatible airfoil candidates found satisfying structural constraints. "
                f"Last validation error: {last_exception}"
            ])

        # Merge analysis warning if any
        if analysis.moment_implication_warning:
            warnings.append(analysis.moment_implication_warning)

        # 9. Compile notes and recommendations
        engineering_notes = [
            f"Root airfoil: {root_airfoil.name} ({root_airfoil.airfoil_type.value}), "
            f"Thickness: {root_airfoil.thickness_ratio*100:.1f}%, Camber: {root_airfoil.camber_ratio*100:.1f}%.",
            f"Tip airfoil: {tip_airfoil.name} ({tip_airfoil.airfoil_type.value}), "
            f"Thickness: {tip_airfoil.thickness_ratio*100:.1f}%, Camber: {tip_airfoil.camber_ratio*100:.1f}%.",
            f"Distribution: {distribution}.",
            f"Cruise profile drag coefficient at root: Cd = {polar_root.cruise_cd:.5f}, L/D = {polar_root.cruise_l_d:.1f}.",
            analysis.analysis_summary,
        ]

        recommendations = strategy.get_recommendations(analysis)

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
            "airfoil_database": "Torq Wings Core library V1",
        }

        # 10. Return compiled AirfoilResult
        return AirfoilResult(
            selected_root_airfoil=root_airfoil.name,
            selected_tip_airfoil=tip_airfoil.name,
            airfoil_distribution=distribution,
            polar_data=polar_root,
            performance_map=performance_map,
            reynolds_analysis=reynolds_data,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
