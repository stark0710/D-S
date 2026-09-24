"""
Fixed-Wing Fuselage Engine Subsystem

Purpose:
    Defines the `FuselageEngine` class, which serves as the orchestrator for the Fuselage Engineering Framework.

Role in Architecture:
    `FuselageEngine` coordinates envelope calculations, component placement, CG balancing,
    mounting interfaces, packing analysis, and validation rules.
"""

from typing import List, Dict, Any
from datetime import datetime

from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements, FuselageType
from backend.design.fixed_wing.fuselage.fuselage_profile import FuselageProfile
from backend.design.fixed_wing.fuselage.fuselage_constraints import FuselageConstraints
from backend.design.fixed_wing.fuselage.fuselage_result import FuselageResult
from backend.design.fixed_wing.fuselage.fuselage_validator import FuselageValidator
from backend.design.fixed_wing.fuselage.fuselage_registry import FuselageStrategyRegistry
from backend.design.fixed_wing.fuselage.fuselage_sizer import FuselageSizer
from backend.design.fixed_wing.fuselage.component_placement import ComponentPlacementService, ComponentPlacement
from backend.design.fixed_wing.fuselage.mounting_interfaces import MountingInterfaces
from backend.design.fixed_wing.fuselage.internal_layout import InternalLayout
from backend.design.fixed_wing.fuselage.fuselage_analysis import FuselageAnalysisService, FuselageAnalysis


class FuselageEngine:
    """
    Facade class managing the fuselage geometry sizing and internal packaging pipeline.
    """

    def __init__(
        self,
        sizer: FuselageSizer | None = None,
        placement_service: ComponentPlacementService | None = None,
        analysis_service: FuselageAnalysisService | None = None,
        validator: FuselageValidator | None = None,
    ) -> None:
        self._sizer = sizer if sizer else FuselageSizer()
        self._placement_service = placement_service if placement_service else ComponentPlacementService()
        self._analysis_service = analysis_service if analysis_service else FuselageAnalysisService()
        self._validator = validator if validator else FuselageValidator()

    def process_fuselage_design(
        self,
        requirements: FuselageRequirements,
        profile: FuselageProfile | None = None,
    ) -> FuselageResult:
        """
        Sizes and integrates the fuselage, compartments, and structural mounts.

        Args:
            requirements (FuselageRequirements): Sizing requirements context.
            profile (FuselageProfile | None): Safety configurations.

        Returns:
            FuselageResult: Sized fuselage layout, CG balance, and analyses.
        """
        if profile is None:
            profile = FuselageProfile()

        m_profile = requirements.mission_result.mission_profile
        wing_geom = requirements.wing_result.wing_geometry
        tail_layout = requirements.tail_result.tail_configuration
        category = m_profile.mission_category

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = FuselageStrategyRegistry.get(strategy_name)

        # 2. Define Fuselage Constraints
        constraints = FuselageConstraints(
            allowed_styles=[FuselageType.CONVENTIONAL, FuselageType.POD_AND_BOOM, FuselageType.TWIN_BOOM],
            min_payload_volume_m3=profile.clearance_margin_m ** 3,
            min_battery_volume_m3=0.0002,
        )

        # 3. Select Fuselage Type using strategy
        fuselage_type = strategy.select_fuselage_type(requirements)

        # 4. Sizing the outer envelope and compartments
        fineness = strategy.get_typical_fineness_ratio()
        cross_section = strategy.get_cross_section_type()

        geometry = self._sizer.size_envelope_dimensions = self._sizer.size_fuselage_envelope(
            requirements=requirements,
            fineness_ratio=fineness,
            clearance_margin=profile.clearance_margin_m,
            cross_section=cross_section,
            fuselage_type=fuselage_type,
        )

        # 5. Sizing mounting interfaces
        interfaces = self._sizer.size_mounting_interfaces(
            geometry=geometry,
            requirements=requirements,
            fuselage_type=fuselage_type,
        )

        # 6. Balance components and calculate CG
        layout = requirements.configuration_result.selected_configuration
        prop_layout = layout.get("propulsion_layout", "Tractor")
        
        placement: ComponentPlacement = self._placement_service.place_components(
            fuselage_length=geometry.length_m,
            wing_x_location=geometry.wing_attachment_x_m,
            wing_mac=wing_geom.mean_aerodynamic_chord_m,
            payload_mass=m_profile.payload_kg,
            battery_mass=1.2,  # Typical battery weight in kg
            propulsion_layout=prop_layout,
        )

        # 7. Create internal layout position registry
        internal_layout = InternalLayout(
            payload_placement_x_m=placement.component_locations["Payload"],
            battery_placement_x_m=placement.component_locations["Battery"],
            flight_controller_placement_x_m=placement.component_locations["FlightController"],
            gps_placement_x_m=placement.component_locations["GPS"],
            receiver_placement_x_m=placement.component_locations["Receiver"],
            telemetry_placement_x_m=placement.component_locations["Telemetry"],
            esc_placement_x_m=placement.component_locations["ESC"],
            power_distribution_location="Fuselage mid-deck floor beneath battery bay",
            cable_routing_path="Bilateral fuselage floor side channels (isolated from ESC power cables)",
            cooling_airflow_channel="Nose cooling duct scoop to rear fuselage side vent exhausts",
            service_access_description="Quick-release top avionics canopy hatch + removable wing saddle floor plate",
        )

        # 8. Detailed packaging and aerodynamic analysis
        analysis = self._analysis_service.analyze_fuselage(
            length=geometry.length_m,
            width=geometry.width_m,
            height=geometry.height_m,
            payload_vol=geometry.payload_bay_volume_m3,
            battery_vol=geometry.battery_bay_volume_m3,
            total_vol=geometry.total_volume_m3,
            tail_style=tail_layout,
            fuselage_type=fuselage_type.value,
        )

        # 9. Validate sized geometry
        warnings = self._validator.validate(
            requirements, constraints, geometry, interfaces, internal_layout, analysis
        )

        # 10. Compile notes and recommendations
        engineering_notes = [
            f"Fuselage type: {fuselage_type.value}.",
            f"Sized length: {geometry.length_m:.2f} m, Width: {geometry.width_m:.2f} m, Height: {geometry.height_m:.2f} m.",
            f"Total fuselage internal volume: {geometry.total_volume_m3:.5f} m3, utilization ratio: {analysis.volume_utilization_ratio*100:.1f}%.",
            f"Balanced CG location: {placement.calculated_cg_x_m:.3f} m from nose, static margin stability: {placement.static_margin_pct:.1f}%.",
        ]
        
        recommendations = strategy.get_recommendations(analysis)

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
        }

        # 11. Return compiled FuselageResult
        return FuselageResult(
            fuselage_geometry=geometry,
            internal_layout=internal_layout,
            component_placement=placement,
            mounting_interfaces=interfaces,
            fuselage_analysis=analysis,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
