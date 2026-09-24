"""
VTOL Lift System Engineering Engine Subsystem

Purpose:
    Defines the `LiftSystemEngine` orchestrator class sizing rotors, motor Kv,
    aerodynamic loading efficiency, ESC thermal currents, and engine failure redundancy.
"""

from typing import List, Dict, Any
import math
from datetime import datetime

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.lift_system.lift_system_requirements import LiftSystemRequirements
from backend.design.vtol.lift_system.lift_system_result import LiftSystemResult
from backend.design.vtol.lift_system.lift_rotor_layout import RotorPlacement, LiftRotorLayout
from backend.design.vtol.lift_system.hover_thrust_analysis import HoverThrustAnalysis
from backend.design.vtol.lift_system.lift_power_analysis import LiftPowerAnalysis
from backend.design.vtol.lift_system.lift_redundancy import LiftRedundancyAnalysis
from backend.design.vtol.lift_system.lift_system_analysis import LiftSystemAnalysis
from backend.design.vtol.lift_system.lift_system_validator import LiftSystemValidator
from backend.design.vtol.lift_system.lift_system_registry import VTOLFiftSystemStrategyRegistry
from backend.design.vtol.lift_system.lift_system_profile import LiftSystemProfile
from backend.design.vtol.lift_system.lift_motor_selector import LiftMotorSelector
from backend.design.vtol.lift_system.lift_propeller_selector import LiftPropellerSelector
from backend.design.vtol.hover_performance.authoritative_hover import AuthoritativeHoverModel


class LiftSystemEngine:
    """
    Facade orchestrator driving lift rotor layout coordinates, sizing, and fail-safe safety audits.
    """

    def __init__(
        self,
        validator: LiftSystemValidator | None = None,
        profile: LiftSystemProfile | None = None,
        motor_selector: LiftMotorSelector | None = None,
        propeller_selector: LiftPropellerSelector | None = None,
    ) -> None:
        self._validator = validator or LiftSystemValidator()
        self._profile = profile or LiftSystemProfile()
        self._motor_selector = motor_selector or LiftMotorSelector()
        self._propeller_selector = propeller_selector or LiftPropellerSelector()

    def design_lift_system(self, requirements: LiftSystemRequirements) -> LiftSystemResult:
        """
        Orchestrates vertical lift system component selection and loading analyses.

        Args:
            requirements (LiftSystemRequirements): Sizing overrides.

        Returns:
            LiftSystemResult: Sized lift system.
        """
        mission_res = requirements.mission_result
        config_res = requirements.configuration_result
        wing_res = requirements.wing_result
        fuse_res = requirements.fuselage_result
        tail_res = requirements.tail_result

        # 1. Select Strategy
        strategy = VTOLFiftSystemStrategyRegistry.get(mission_res.mission_profile.mission_category)

        # 2. Sizing mass & thrust sizing factors
        mtow = mission_res.mission_analysis.estimated_mtow_kg
        f_safety = strategy.default_safety_factor
        if hasattr(requirements, "metadata") and "hover_thrust_to_weight_target" in requirements.metadata:
            f_safety = float(requirements.metadata["hover_thrust_to_weight_target"])
        elif hasattr(mission_res, "mission_requirements") and hasattr(mission_res.mission_requirements, "metadata"):
            meta = mission_res.mission_requirements.metadata or {}
            if "hover_thrust_to_weight_target" in meta:
                f_safety = float(meta["hover_thrust_to_weight_target"])

        # 3. Retrieve configuration settings from authoritative configuration
        vtol_config = getattr(config_res, "vtol_configuration", None)
        if vtol_config is not None:
            motor_count = vtol_config.lift_motor_count
        elif hasattr(config_res, "lift_architecture") and config_res.lift_architecture:
            motor_count = config_res.lift_architecture.motor_count
        else:
            motor_count = 4

        if motor_count <= 0:
            motor_count = 4

        is_coaxial = False
        if hasattr(config_res, "lift_architecture") and config_res.lift_architecture:
            is_coaxial = "coaxial" in config_res.lift_architecture.lift_system_type.lower()
        elif vtol_config is not None:
            is_coaxial = vtol_config.has_coaxial_rotors

        coaxial_loss = 0.15 if is_coaxial else 0.0
        coaxial_correction = 1.0 - (0.5 * coaxial_loss)

        # Preliminary thrust requirement for motor sizing
        weight_prelim = mtow * 9.80665
        req_thrust_prelim = weight_prelim * f_safety
        req_thrust_per_rotor_prelim = (req_thrust_prelim / motor_count) / coaxial_correction

        # 4. Select motor & propeller based on thrust and disk loading constraints
        qualified_names = self._motor_selector.get_all_motors()
        qualified_motors = [self._motor_selector.get_motor(name) for name in qualified_names]
        qualified_motors = [m for m in qualified_motors if m and m["max_thrust_n"] >= req_thrust_per_rotor_prelim]
        qualified_motors = sorted(qualified_motors, key=lambda x: x["mass_kg"])

        motor = qualified_motors[0] if qualified_motors else self._motor_selector.get_motor("Hobbywing XRotor 10120")
        propeller = self._propeller_selector.select_optimal_propeller(motor["name"])

        max_dl_limit = requirements.metadata.get("max_disk_loading", 150.0)
        for m_candidate in qualified_motors:
            prop_candidate = self._propeller_selector.select_optimal_propeller(m_candidate["name"])
            total_disk_area_cand = motor_count * (0.25 * math.pi * prop_candidate["diameter_m"]**2)
            disk_loading_cand = weight_prelim / total_disk_area_cand
            if disk_loading_cand <= max_dl_limit:
                motor = m_candidate
                propeller = prop_candidate
                break

        # Authoritative rotor diameter and voltage
        prop_diam = propeller["diameter_m"]
        req_diam = requirements.metadata.get("rotor_diameter_m")
        if req_diam is not None:
            prop_diam = float(req_diam)
        elif hasattr(mission_res, "mission_requirements") and hasattr(mission_res.mission_requirements, "metadata"):
            meta = mission_res.mission_requirements.metadata or {}
            if "rotor_diameter_m" in meta:
                prop_diam = float(meta["rotor_diameter_m"])

        v_nom = self._profile.battery_nominal_voltage_v
        req_volt = requirements.metadata.get("system_voltage_v")
        if req_volt is not None:
            v_nom = float(req_volt)
        elif hasattr(mission_res, "mission_requirements") and hasattr(mission_res.mission_requirements, "metadata"):
            meta = mission_res.mission_requirements.metadata or {}
            if "system_voltage_v" in meta:
                v_nom = float(meta["system_voltage_v"])

        # Execute single Authoritative Hover Physics Engine
        auth_hover = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=mtow,
            lift_motor_count=motor_count,
            rotor_diameter_m=prop_diam,
            system_voltage_v=v_nom,
            hover_thrust_to_weight_target=f_safety,
        )

        weight_n = auth_hover.aircraft_weight_n
        req_thrust_total = auth_hover.required_total_hover_thrust_n

        # 5. Sizing Available Thrust
        max_thrust_per_motor = motor["max_thrust_n"]
        avail_thrust_total = motor_count * max_thrust_per_motor * coaxial_correction
        thrust_to_weight = avail_thrust_total / weight_n
        thrust_margin = avail_thrust_total - weight_n

        hover_thrust_analysis = HoverThrustAnalysis(
            required_hover_thrust_n=round(req_thrust_total, 1),
            available_hover_thrust_n=round(avail_thrust_total, 1),
            thrust_to_weight_ratio=round(thrust_to_weight, 2),
            thrust_margin_n=round(thrust_margin, 1),
        )

        # 6. Sizing Layout Coordinates
        span = wing_res.wing_geometry.span_m
        f_len = fuse_res.fuselage_geometry.length_m
        y_mount = span * 0.28
        x_mount = f_len * 0.26

        rotors: List[RotorPlacement] = []
        if is_coaxial:
            boom_count = motor_count // 2
            orientations = ["CW", "CCW"] * boom_count
            locations = [
                ("Front Left", x_mount, -y_mount),
                ("Front Right", x_mount, y_mount),
                ("Rear Left", -x_mount, -y_mount),
                ("Rear Right", -x_mount, y_mount),
            ]
            r_idx = 0
            for loc_name, lx, ly in locations[:boom_count]:
                rotors.append(RotorPlacement(
                    name=f"{loc_name} Upper Rotor",
                    motor_model=motor["name"],
                    propeller_model=propeller["name"],
                    x_m=round(lx, 3),
                    y_m=round(ly, 3),
                    z_m=0.08,
                    orientation=orientations[r_idx],
                ))
                rotors.append(RotorPlacement(
                    name=f"{loc_name} Lower Rotor",
                    motor_model=motor["name"],
                    propeller_model=propeller["name"],
                    x_m=round(lx, 3),
                    y_m=round(ly, 3),
                    z_m=-0.08,
                    orientation="CCW" if orientations[r_idx] == "CW" else "CW",
                ))
                r_idx += 1
            spacing = 0.0
        else:
            if motor_count == 4:
                locations = [
                    ("Front Left", x_mount, -y_mount, "CW"),
                    ("Front Right", x_mount, y_mount, "CCW"),
                    ("Rear Left", -x_mount, -y_mount, "CCW"),
                    ("Rear Right", -x_mount, y_mount, "CW"),
                ]
            else:
                locations = []
                for i in range(motor_count):
                    angle = (2.0 * math.pi * i) / motor_count
                    r_len = max(x_mount, y_mount) * 0.9
                    lx = r_len * math.cos(angle)
                    ly = r_len * math.sin(angle)
                    orient = "CW" if i % 2 == 0 else "CCW"
                    locations.append((f"Rotor {i+1}", lx, ly, orient))

            for loc_name, lx, ly, orient in locations:
                rotors.append(RotorPlacement(
                    name=f"{loc_name} Rotor",
                    motor_model=motor["name"],
                    propeller_model=propeller["name"],
                    x_m=round(lx, 3),
                    y_m=round(ly, 3),
                    z_m=0.0,
                    orientation=orient,
                ))

            spacing = round(math.sqrt((2.0 * x_mount)**2), 3)

        rotor_layout = LiftRotorLayout(
            rotors=rotors,
            rotor_spacing_m=spacing,
            distributed_propulsion_active=motor_count >= 8 and not is_coaxial,
        )

        # 7. Sizing Power Consumption & Battery current draws via AuthoritativeHoverModel
        total_hover_power_kw = (auth_hover.hover_electrical_power_w or 0.0) / 1000.0
        total_hover_current = auth_hover.hover_current_a or ((total_hover_power_kw * 1000.0) / v_nom)
        esc_current = auth_hover.hover_current_per_motor_a or (total_hover_current / motor_count)

        energy_demand = mission_res.mission_profile.total_energy_demand_kwh
        battery_capacity_ah = (energy_demand * 1000.0) / v_nom
        required_c_rate = total_hover_current / max(0.5, battery_capacity_ah)

        hover_duration_hr = mission_res.hover_requirements.hover_duration_min / 60.0
        hover_energy_kwh = total_hover_power_kw * hover_duration_hr

        power_analysis = LiftPowerAnalysis(
            hover_total_power_kw=round(total_hover_power_kw, 2),
            hover_total_current_a=round(total_hover_current, 1),
            hover_energy_consumption_kwh=round(hover_energy_kwh, 3),
            esc_current_draw_a=round(esc_current, 1),
            battery_c_rate_required=round(required_c_rate, 2),
        )

        # 8. Sizing Redundancy reserves
        avail_motors = motor_count - 1
        oei_avail_thrust = avail_motors * max_thrust_per_motor * coaxial_correction
        has_oei = oei_avail_thrust >= weight_n
        oei_margin_fraction = (oei_avail_thrust - weight_n) / weight_n

        redundancy_level = "Single Motor Out Controllable" if (has_oei and motor_count >= 6) else "No redundancy (thrust loss hazard)"
        scenarios = ["Front Left Rotor Loss", "Rear Right Rotor Loss"]

        redundancy = LiftRedundancyAnalysis(
            redundancy_level=redundancy_level,
            has_engine_out_capability=has_oei,
            motor_out_thrust_reserve_fraction=round(oei_margin_fraction, 2),
            failure_scenarios_tested=scenarios,
        )

        # 9. Sizing Loading Analysis (Disk loading, efficiency)
        total_disk_area = auth_hover.total_disk_area_m2 or (motor_count * (0.25 * math.pi * prop_diam**2))
        disk_loading = auth_hover.disk_loading_n_m2 or (weight_n / total_disk_area)
        power_loading = weight_n / (total_hover_power_kw * 1000.0) if total_hover_power_kw > 0 else 0.0
        hover_g_w = (weight_n / (total_hover_power_kw * 1000.0)) * (1000.0 / 9.80665) if total_hover_power_kw > 0 else 7.0

        noise = 65.0 + 10.0 * math.log10(disk_loading)

        analysis = LiftSystemAnalysis(
            disk_loading_n_m2=round(disk_loading, 2),
            power_loading_n_w=round(power_loading, 4),
            hover_efficiency_g_w=round(hover_g_w, 2),
            rotor_interference_loss_factor=coaxial_loss,
            noise_level_db=round(noise, 1),
            manufacturability_score=85.0 if motor_count <= 4 else 75.0,
            fault_tolerance_score=90.0 if has_oei else 50.0,
        )

        # 10. Technical Requirements (Manufacturer-Independent Output)
        tech_reqs = {
            "lift_motor_count": motor_count,
            "sizing_mass_kg": round(mtow, 4),
            "aircraft_weight_n": round(auth_hover.aircraft_weight_n, 3),
            "required_total_hover_thrust_n": round(auth_hover.required_total_hover_thrust_n, 3),
            "required_thrust_per_motor_n": round(auth_hover.required_thrust_per_motor_n, 3),
            "thrust_to_weight_target": round(f_safety, 3),
            "thrust_margin_n": round(auth_hover.thrust_margin_n, 3),
            "thrust_margin_ratio": round(auth_hover.thrust_margin_ratio, 3),
            "rotor_diameter_m": round(auth_hover.rotor_diameter_m, 4) if auth_hover.rotor_diameter_m is not None else None,
            "total_disk_area_m2": round(auth_hover.total_disk_area_m2, 4) if auth_hover.total_disk_area_m2 is not None else None,
            "disk_loading_n_m2": round(auth_hover.disk_loading_n_m2, 3) if auth_hover.disk_loading_n_m2 is not None else None,
            "required_hover_power_w": round(auth_hover.hover_electrical_power_w, 2) if auth_hover.hover_electrical_power_w is not None else None,
            "required_hover_power_per_motor_w": round(auth_hover.hover_power_per_motor_w, 2) if auth_hover.hover_power_per_motor_w is not None else None,
            "system_voltage_v": round(v_nom, 2),
            "required_hover_current_a": round(auth_hover.hover_current_a, 2) if auth_hover.hover_current_a is not None else None,
            "required_current_per_motor_a": round(auth_hover.hover_current_per_motor_a, 2) if auth_hover.hover_current_per_motor_a is not None else None,
            "coaxial_thrust_correction": round(coaxial_correction, 3),
            "is_converged_mtow": auth_hover.is_converged_mtow,
            "mtow_status": auth_hover.mtow_status,
        }

        # 11. Compile Notes, warnings and recommendations
        notes = [
            f"Lift system sized for {motor_count} lift motors with {req_thrust_per_rotor_prelim:.1f} N required per motor.",
            f"Advisory catalog match: {motor['name']} brushless motors with {propeller['name']} propellers.",
            f"Total available vertical hover thrust: {avail_thrust_total:.1f} N (safety factor: {thrust_to_weight:.2f} G).",
        ]

        recs = strategy.get_recommendations()
        warnings: List[str] = list(auth_hover.warnings)

        if disk_loading > 120.0:
            warnings.append("High disk loading. Hover efficiency is low, causing high thermal ESC current draw.")
        if not has_oei:
            warnings.append("No engine out redundancy. Motor loss will cause immediate loss of hover control.")

        result = LiftSystemResult(
            lift_motor_selection=motor,
            lift_propeller_selection=propeller,
            rotor_layout=rotor_layout,
            hover_analysis=hover_thrust_analysis,
            power_analysis=power_analysis,
            redundancy_analysis=redundancy,
            engineering_analysis=analysis,
            authoritative_result=auth_hover,
            technical_requirements=tech_reqs,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
            metadata={
                "strategy_applied": strategy.__class__.__name__,
            },
        )

        # 12. Run validations (raises error if invalid)
        self._validator.validate(requirements, result)

        meta = {
            "engine_version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        }
        result.metadata.update(meta)

        return result
