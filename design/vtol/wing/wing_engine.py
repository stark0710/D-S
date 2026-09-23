"""
VTOL Wing Sizing Engine Subsystem

Purpose:
    Defines the `WingEngine` facade class orchestrating wing planform sizing,
    aerodynamic lift coefficients, root bending moments, and pylon mounts.
"""

from typing import List, Dict, Any
import math
from datetime import datetime

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.wing.wing_requirements import WingRequirements
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.wing.wing_geometry import WingGeometry
from backend.design.vtol.wing.wing_structure import WingStructure
from backend.design.vtol.wing.wing_mounts import MotorMount, MotorMounts
from backend.design.vtol.wing.wing_analysis import WingAnalysis
from backend.design.vtol.wing.wing_validator import WingValidator
from backend.design.vtol.wing.wing_registry import VTOLWingStrategyRegistry
from backend.design.vtol.wing.wing_sizer import WingSizer


class WingEngine:
    """
    Facade orchestrator driving wing geometry, structures, and mounts sizing loops.
    """

    def __init__(
        self,
        validator: WingValidator | None = None,
        sizer: WingSizer | None = None,
    ) -> None:
        self._validator = validator or WingValidator()
        self._sizer = sizer or WingSizer()

    def size_wing_system(self, requirements: WingRequirements) -> WingResult:
        """
        Orchestrates the complete wing system sizing process.

        Args:
            requirements (WingRequirements): Overrides and preceding stage outputs.

        Returns:
            WingResult: Complete wing definition.
        """
        mission_res = requirements.mission_result
        config_res = requirements.configuration_result

        # 1. Retrieve appropriate wing strategy
        strategy = VTOLWingStrategyRegistry.get(mission_res.mission_profile.mission_category)

        # 2. Solver sizing
        mtow = mission_res.mission_analysis.estimated_mtow_kg
        taper = requirements.metadata.get("taper_ratio", 0.6)

        sized = self._sizer.size_wing(
            mtow_kg=mtow,
            target_loading=strategy.default_wing_loading_kg_m2,
            target_ar=strategy.default_aspect_ratio,
            taper_ratio=taper,
            override_span=requirements.preferred_wing_span_m,
            override_ar=requirements.preferred_aspect_ratio,
        )

        # 3. Determine Wing Type
        wing_type = requirements.preferred_wing_type
        if wing_type is None:
            if config_res.selected_configuration == VTOLType.TILT_WING:
                wing_type = "Tilt Wing"
            elif config_res.selected_configuration == VTOLType.BOX_WING_VTOL:
                wing_type = "Box Wing"
            elif config_res.selected_configuration == VTOLType.TWIN_BOOM_VTOL:
                wing_type = "Twin Boom Wing"
            else:
                wing_type = strategy.default_wing_position

        # 4. Assemble Geometry
        geom = WingGeometry(
            wing_type=wing_type,
            span_m=sized["span_m"],
            area_m2=sized["area_m2"],
            aspect_ratio=sized["aspect_ratio"],
            sweep_deg=strategy.default_sweep_deg,
            dihedral_deg=strategy.default_dihedral_deg,
            anhedral_deg=0.0,
            incidence_deg=requirements.metadata.get("incidence_deg", 2.0),
            washout_deg=requirements.metadata.get("washout_deg", 1.5),
            taper_ratio=taper,
            root_chord_m=sized["root_chord_m"],
            tip_chord_m=sized["tip_chord_m"],
            wing_position=strategy.default_wing_position,
        )

        # 5. Compile Motor Mounts from Configuration Placements
        mount_list: List[MotorMount] = []
        placements = config_res.actuator_layout.actuator_placements

        # Extract motor coordinate mappings on wings
        for idx, plac in enumerate(placements):
            # Motors are typically named "Motor" or "Hover" or "Tilt"
            if "Motor" in plac["name"] or "Tilt" in plac["name"]:
                # If motor has a non-zero Y spanwise coordinate, it is wing/boom mounted
                if abs(plac["y_m"]) > 0.05:
                    mount_list.append(
                        MotorMount(
                            name=f"Wing Mount - {plac['name']}",
                            motor_index=idx,
                            position_x_m=plac["x_m"],
                            position_y_m=plac["y_m"],
                            position_z_m=plac["z_m"],
                            mount_type="Tilt Servo Pivot" if "Tilt" in plac["name"] else "Boom Sleeve Clamp",
                            estimated_mass_kg=round(mtow * 0.015, 3),  # Mount structure scales with MTOW
                            max_thrust_n_limit=round(mtow * 9.80665 * 1.5, 1),
                        )
                    )

        has_tilt = config_res.selected_configuration in (VTOLType.TILT_ROTOR, VTOLType.TILT_WING)
        tilt_torque = round(mtow * 0.45, 2) if has_tilt else 0.0

        mounts = MotorMounts(
            mounts=mount_list,
            has_tilt_mechanism=has_tilt,
            tilt_servo_torque_nm=tilt_torque,
        )

        # 6. Wing Structure
        struct = WingStructure(
            structural_concept=strategy.structural_concept,
            estimated_wing_weight_kg=sized["wing_weight_kg"],
            limit_load_factor_g=4.0,
            ultimate_load_factor_g=6.0,
            spar_material="Ultra-high-modulus Carbon Fiber" if mtow > 15.0 else "Aircraft Balsa/Spruce laminate",
        )

        # 7. Aerodynamic and structural checks
        rho_cruise = mission_res.mission_profile.air_density_cruise_kg_m3
        v_cruise = mission_res.cruise_requirements.cruise_speed_kmh / 3.6

        # CL_cruise = L / (0.5 * rho * V^2 * S)
        dynamic_pressure = 0.5 * rho_cruise * (v_cruise ** 2)
        cl_cruise = (mtow * 9.80665) / (dynamic_pressure * sized["area_m2"])

        # Stall speed: V_stall = sqrt(2*W / (rho * Cl_max * S))
        cl_max = 1.35
        v_stall_m_s = math.sqrt((2.0 * mtow * 9.80665) / (rho_cruise * cl_max * sized["area_m2"]))
        v_stall_kmh = v_stall_m_s * 3.6

        # Peak transition bending moment (root bending)
        # Sized using simple spar load distribution: lift force on one wing * semi-span centroids
        trans_bending = (mtow * 9.80665 / 2.0) * (sized["span_m"] / 4.0) * 1.35

        # Trade-offs scores
        if config_res.selected_configuration == VTOLType.TILT_WING:
            mfg_score = 65.0
            m_integration = 60.0
            maint_score = 55.0
        elif config_res.selected_configuration == VTOLType.LIFT_CRUISE:
            mfg_score = 85.0
            m_integration = 85.0
            maint_score = 80.0
        else:
            mfg_score = 75.0
            m_integration = 75.0
            maint_score = 70.0

        analysis = WingAnalysis(
            wing_loading_kg_m2=round(mtow / sized["area_m2"], 2),
            cruise_lift_coefficient=round(cl_cruise, 3),
            stall_speed_cruise_configuration_kmh=round(v_stall_kmh, 2),
            cruise_efficiency=85.0 if geom.aspect_ratio > 12.0 else 70.0,
            hover_structural_loading=round(mtow * 0.1, 2),
            transition_bending_moment_nm=round(trans_bending, 2),
            structural_efficiency=round(100.0 - (struct.estimated_wing_weight_kg / mtow) * 100.0, 1),
            manufacturability_score=mfg_score,
            motor_integration_score=m_integration,
            maintenance_accessibility_score=maint_score,
        )

        # 8. Run validations
        self._validator.validate(requirements, geom, mounts)

        # 9. Formulate warnings, notes, recs
        notes = [
            f"Wing planform area sized: {geom.area_m2:.4f} m².",
            f"Calculated cruise lift coefficient: {analysis.cruise_lift_coefficient:.3f}.",
            f"Estimated root bending moment under transition loads: {analysis.transition_bending_moment_nm:.2f} Nm.",
        ]

        recs = strategy.get_recommendations(geom)
        warnings: List[str] = []
        if analysis.wing_loading_kg_m2 > 50.0:
            warnings.append(f"High wing loading ({analysis.wing_loading_kg_m2:.1f} kg/m²). This increases transition stall speed.")

        meta = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.__class__.__name__,
        }

        return WingResult(
            wing_geometry=geom,
            wing_structure=struct,
            motor_mounts=mounts,
            wing_analysis=analysis,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
            metadata=meta,
        )
