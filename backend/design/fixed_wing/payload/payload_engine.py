"""
Fixed-Wing Payload Engine Subsystem

Purpose:
    Defines the `PayloadEngine` class, which serves as the orchestrator for the Payload Engineering Framework.

Role in Architecture:
    `PayloadEngine` coordinates sizers, selectors, packaging, dynamic CG shift evaluations,
    and validation rules to integrate mission equipment.
"""

from typing import List, Dict, Any
from datetime import datetime

from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements, PayloadType
from backend.design.fixed_wing.payload.payload_profile import PayloadProfile
from backend.design.fixed_wing.payload.payload_constraints import PayloadConstraints
from backend.design.fixed_wing.payload.payload_result import PayloadResult
from backend.design.fixed_wing.payload.payload_validator import PayloadValidator
from backend.design.fixed_wing.payload.payload_registry import PayloadStrategyRegistry
from backend.design.fixed_wing.payload.payload_selector import PayloadSelector, PayloadRecord
from backend.design.fixed_wing.payload.payload_mount import PayloadMount
from backend.design.fixed_wing.payload.payload_layout import PayloadLayout
from backend.design.fixed_wing.payload.payload_power import PayloadPowerInterface
from backend.design.fixed_wing.payload.payload_data import PayloadDataInterface
from backend.design.fixed_wing.payload.payload_cooling import PayloadCooling
from backend.design.fixed_wing.payload.payload_analysis import PayloadAnalysis, PayloadAnalysisService


class PayloadEngine:
    """
    Orchestration facade sizing, arranging, and balancing payload payloads.
    """

    def __init__(
        self,
        selector: PayloadSelector | None = None,
        analysis_service: PayloadAnalysisService | None = None,
        validator: PayloadValidator | None = None,
    ) -> None:
        self._selector = selector if selector else PayloadSelector()
        self._analysis_service = analysis_service if analysis_service else PayloadAnalysisService()
        self._validator = validator if validator else PayloadValidator()

    def process_payload_design(
        self,
        requirements: PayloadRequirements,
        profile: PayloadProfile | None = None,
    ) -> PayloadResult:
        """
        Integrates, locates, and validates aircraft payloads.

        Args:
            requirements (PayloadRequirements): Sizing requirements context.
            profile (PayloadProfile | None): Safety configurations.

        Returns:
            PayloadResult: Integrated components, power/data interfaces, and CG analysis.
        """
        if profile is None:
            profile = PayloadProfile()

        m_profile = requirements.mission_result.mission_profile
        category = m_profile.mission_category
        f_geom = requirements.fuselage_result.fuselage_geometry
        wing_geom = requirements.wing_result.wing_geometry
        mtow = None
        for val in [
            getattr(m_profile, "current_iteration_mtow_kg", None),
            getattr(m_profile, "initial_mtow_seed_kg", None),
            getattr(getattr(requirements, "mission_result", None), "constraints", None) and getattr(requirements.mission_result.constraints, "maximum_takeoff_weight_kg", None),
        ]:
            if isinstance(val, (int, float)) and val > 0.0:
                mtow = float(val)
                break
        if mtow is None:
            p_kg = getattr(m_profile, "payload_kg", 1.0)
            if isinstance(p_kg, (int, float)):
                mtow = max(2.0, float(p_kg) * 3.5)
            else:
                mtow = 5.0

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = PayloadStrategyRegistry.get(strategy_name)

        # 2. Define Constraints
        constraints = PayloadConstraints(
            allowed_types=[PayloadType.RGB_CAMERA, PayloadType.MULTISPECTRAL, PayloadType.CARGO, PayloadType.LIDAR],
            max_payload_weight_kg=m_profile.payload_kg * 1.05,
            max_payload_power_w=30.0,
            max_bandwidth_mbps=15.0,
        )

        # 3. Select payloads based on strategy
        target_types = strategy.select_payloads(requirements)
        selected_records: List[PayloadRecord] = []
        for p_type in target_types:
            record = self._selector.select_payload(
                p_type,
                constraints.max_payload_weight_kg,
                target_weight_kg=m_profile.payload_kg,
            )
            selected_records.append(record)

        total_weight = sum(r.weight_kg for r in selected_records)
        total_vol = sum((r.dimensions_mm[0]*r.dimensions_mm[1]*r.dimensions_mm[2])/1e9 for r in selected_records)

        # 4. Sizing coordinate locations (close to aerodynamic center to minimize pitch trim offset)
        # Sized coordinate center X: place it slightly in front of quarter chord
        placement_x = wing_geom.quarter_chord_x_m - 0.015

        # Compartment volume
        comp_len = f_geom.payload_bay_length_m
        comp_width = f_geom.payload_bay_width_m
        comp_height = f_geom.payload_bay_height_m
        compartment_vol = comp_len * comp_width * comp_height

        # Layout guidelines from strategy
        orient, access = strategy.get_layout_guidelines()
        layout = PayloadLayout(
            placement_x_m=round(placement_x, 3),
            orientation=orient,
            compartment_length_m=round(comp_len, 3),
            compartment_width_m=round(comp_width, 3),
            compartment_height_m=round(comp_height, 3),
            accessibility_description=access,
        )

        # 5. Create payload mounts
        mounts_list: List[PayloadMount] = []
        mount_style = strategy.get_mount_style()
        is_gimbal = "gimbal" in mount_style.lower()
        
        mounts_list.append(
            PayloadMount(
                mount_style=mount_style,
                vibration_isolation_type="Alpha-gel compression dampers",
                isolation_frequency_hz=profile.vibration_damping_frequency_hz,
                mounting_hardware="4x M3 carbon plate bolts",
                tilt_angle_limit_deg=45.0 if is_gimbal else 0.0,
            )
        )

        # 6. Create power interfaces
        power_list: List[PayloadPowerInterface] = []
        for r in selected_records:
            reg_req = r.power_w >= 10.0
            power_list.append(
                PayloadPowerInterface(
                    voltage_v=12.0 if r.power_w >= 10.0 else profile.standard_voltage_v,
                    max_current_a=round(r.power_w / (12.0 if r.power_w >= 10.0 else profile.standard_voltage_v), 2) if r.power_w > 0 else 0.0,
                    connector_type="XT30" if r.power_w >= 10.0 else "JST-GH",
                    regulator_required=reg_req,
                    power_draw_w=r.power_w,
                )
            )

        # 7. Create data interfaces
        data_list: List[PayloadDataInterface] = []
        for r in selected_records:
            data_list.append(
                PayloadDataInterface(
                    interface_type="Ethernet RJ45" if r.bandwidth_mbps >= 5.0 else "USB-C",
                    bandwidth_mbps=r.bandwidth_mbps,
                    geotagging_protocol="Mavlink CAMERA_FEEDBACK" if r.payload_type == PayloadType.RGB_CAMERA else "None",
                    datalogger_storage_gb=64.0 if r.bandwidth_mbps > 0 else 0.0,
                )
            )

        # 8. Sizing cooling requirements
        total_power = sum(r.power_w for r in selected_records)
        cooling_style = "Passive heat-sink"
        if total_power >= 12.0:
            cooling_style = "Forced convection air scoop"
            
        intake_area = (total_power * 8.0) * profile.cooling_margin_factor if total_power > 0 else 0.0
        cooling = PayloadCooling(
            heat_dissipation_w=round(total_power * profile.cooling_margin_factor, 1),
            cooling_type=cooling_style,
            required_intake_area_mm2=round(intake_area, 1),
            operating_temp_max_c=60.0,
        )

        # 9. Perform detailed CG shift analysis
        # Calculated empty CG is typically close to wing quarter chord location
        calculated_cg = wing_geom.quarter_chord_x_m
        
        analysis = self._analysis_service.analyze_payload_integration(
            payloads=selected_records,
            placement_x_m=placement_x,
            cg_calculated_x_m=calculated_cg,
            wing_mac=wing_geom.mean_aerodynamic_chord_m,
            mtow_kg=mtow,
            compartment_vol=compartment_vol,
        )

        # 10. Validate integration layout
        warnings = self._validator.validate(
            requirements=requirements,
            constraints=constraints,
            profile=profile,
            selected_payloads_weight=total_weight,
            selected_payloads_vol=total_vol,
            compartment_vol=compartment_vol,
            analysis=analysis,
        )

        # 11. Compile notes and recommendations
        selected_names = [r.name for r in selected_records]
        engineering_notes = [
            f"Payload strategy applied: {strategy.name}.",
            f"Selected payloads: {', '.join(selected_names)}.",
            f"compartment volume utilization: {round((total_vol / compartment_vol)*100.0, 1)}%.",
            f"CG displacement: {analysis.cg_shift_offset_m*1000:.1f} mm, static margin shift: {analysis.static_margin_impact_pct:.2f}%.",
            f"Continuous thermal load: {total_power:.1f} W, cooling style: {cooling_style}.",
        ]
        
        recommendations = strategy.get_recommendations()

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
        }

        # Sized/installed payload mass vs requested
        requested_mass = m_profile.payload_kg
        if category.value == "Cargo" if hasattr(category, "value") else category == "Cargo":
            installed_mass = requested_mass
        else:
            installed_mass = max(requested_mass, total_weight)
        design_margin = max(0.0, installed_mass - requested_mass)

        # 12. Return compiled PayloadResult
        return PayloadResult(
            selected_payloads=selected_names,
            payload_layout=layout,
            payload_mounts=mounts_list,
            power_interfaces=power_list,
            communication_interfaces=data_list,
            cooling_requirements=cooling,
            payload_analysis=analysis,
            requested_payload_mass_kg=requested_mass,
            installed_payload_mass_kg=installed_mass,
            payload_design_margin_kg=design_margin,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
