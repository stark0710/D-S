"""
VTOL Forward Propulsion Sizing Engine Subsystem

Purpose:
    Defines the `ForwardPropulsionEngine` facade class orchestrating aerodynamic drag sizing,
    required cruise thrust, motor and prop selectors, dynamic speed ceilings,
    climb authorities, and validations.
"""

from typing import List, Dict, Any
import math
from datetime import datetime

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.forward_propulsion.forward_propulsion_requirements import ForwardPropulsionRequirements
from backend.design.vtol.forward_propulsion.forward_propulsion_result import ForwardPropulsionResult
from backend.design.vtol.forward_propulsion.propulsion_layout import ForwardPlacement, ForwardPropulsionLayout
from backend.design.vtol.forward_propulsion.forward_propulsion_analysis import ForwardPropulsionAnalysis
from backend.design.vtol.forward_propulsion.cruise_power_analysis import CruisePowerAnalysis
from backend.design.vtol.forward_propulsion.cruise_performance_analysis import CruisePerformanceAnalysis
from backend.design.vtol.forward_propulsion.forward_propulsion_validator import ForwardPropulsionValidator
from backend.design.vtol.forward_propulsion.forward_propulsion_registry import VTOLForwardPropulsionStrategyRegistry
from backend.design.vtol.forward_propulsion.forward_propulsion_profile import ForwardPropulsionProfile
from backend.design.vtol.forward_propulsion.cruise_motor_selector import CruiseMotorSelector
from backend.design.vtol.forward_propulsion.cruise_propeller_selector import CruisePropellerSelector
from backend.design.vtol.forward_propulsion.cruise_esc_selector import CruiseEscSelector


class ForwardPropulsionEngine:
    """
    Facade orchestrator driving forward thrust layouts, sizing, and clearances.
    """

    def __init__(
        self,
        validator: ForwardPropulsionValidator | None = None,
        profile: ForwardPropulsionProfile | None = None,
        motor_selector: CruiseMotorSelector | None = None,
        propeller_selector: CruisePropellerSelector | None = None,
        esc_selector: CruiseEscSelector | None = None,
    ) -> None:
        self._validator = validator or ForwardPropulsionValidator()
        self._profile = profile or ForwardPropulsionProfile()
        self._motor_selector = motor_selector or CruiseMotorSelector()
        self._propeller_selector = propeller_selector or CruisePropellerSelector()
        self._esc_selector = esc_selector or CruiseEscSelector()

    def design_forward_propulsion(self, requirements: ForwardPropulsionRequirements) -> ForwardPropulsionResult:
        """
        Orchestrates forward propulsion selection and performance analysis.

        Args:
            requirements (ForwardPropulsionRequirements): Sizing overrides.

        Returns:
            ForwardPropulsionResult: Sized forward propulsion.
        """
        mission_res = requirements.mission_result
        config_res = requirements.configuration_result
        wing_res = requirements.wing_result
        airfoil_res = requirements.airfoil_result
        fuse_res = requirements.fuselage_result
        lift_res = requirements.lift_system_result

        # 1. Strategy selection
        strategy = VTOLForwardPropulsionStrategyRegistry.get(mission_res.mission_profile.mission_category)

        # 2. Sizing total drag coefficient
        # Cd_total = Cd0_wing + Cdi + Cd0_fuse
        cd0_wing = airfoil_res.polar_analysis.cd_cruise
        cl_cruise = wing_res.wing_analysis.cruise_lift_coefficient
        ar = wing_res.wing_geometry.aspect_ratio
        # Assume Oswald efficiency factor e = 0.82 for simple layouts
        cdi = (cl_cruise**2) / (math.pi * 0.82 * ar)
        cd0_fuse = fuse_res.engineering_analysis.aerodynamic_drag_coefficient_cd0

        cd_total = cd0_wing + cdi + cd0_fuse

        # 3. Sizing required cruise thrust ( opposes drag )
        v_cruise = mission_res.cruise_requirements.cruise_speed_kmh / 3.6
        rho = mission_res.mission_profile.air_density_cruise_kg_m3
        s_wing = wing_res.wing_geometry.area_m2

        drag_n = 0.5 * rho * (v_cruise**2) * s_wing * cd_total
        req_thrust = drag_n

        # 4. Sizing required cruise electric power
        # P_mech = T * V
        p_mech = req_thrust * v_cruise
        eta_prop = self._profile.nominal_propeller_efficiency
        eta_motor = self._profile.nominal_motor_efficiency
        p_elec = p_mech / (eta_prop * eta_motor)

        # 5. Retrieve architecture count
        arch = strategy.default_propulsion_architecture
        prop_count = 2 if "twin" in arch.lower() else 1
        power_per_motor = p_elec / prop_count

        # 6. Select motor, propeller, ESC
        motor = self._motor_selector.select_optimal_motor(
            power_per_motor, requirements.preferred_cruise_motor
        )
        propeller = self._propeller_selector.select_optimal_propeller(
            motor["name"], requirements.preferred_cruise_propeller
        )
        esc = self._esc_selector.select_optimal_esc(
            motor["max_current_a"], requirements.preferred_cruise_esc
        )

        # 7. Sizing Available Thrust
        # max available thrust per motor scales with max power rating
        max_avail_power_w = motor["max_power_w"]
        avail_thrust_per_motor = (max_avail_power_w * eta_prop * eta_motor) / max(1.0, v_cruise)
        avail_thrust_total = prop_count * avail_thrust_per_motor

        static_thrust_total = prop_count * (max_avail_power_w * 0.015 * 9.80665)  # static thrust estimate ~15g/W

        analysis = ForwardPropulsionAnalysis(
            required_thrust_n=round(req_thrust, 1),
            available_thrust_n=round(avail_thrust_total, 1),
            static_thrust_n=round(static_thrust_total, 1),
            noise_level_db=round(70.0 + 10.0 * math.log10(req_thrust), 1),
            thermal_temperature_c=65.0,
        )

        # 8. Sizing Electric currents
        mtow = mission_res.mission_analysis.estimated_mtow_kg
        v_nom = lift_res.power_analysis.metadata.get("nominal_voltage", 44.4)
        cruise_current = p_elec / v_nom
        esc_current = cruise_current / prop_count

        # Estimate required battery C-rate contribution during cruise
        energy_demand = mission_res.mission_profile.total_energy_demand_kwh
        battery_capacity_ah = (energy_demand * 1000.0) / v_nom
        required_c_rate = cruise_current / max(0.5, battery_capacity_ah)

        power_analysis = CruisePowerAnalysis(
            required_cruise_power_w=round(p_elec, 1),
            current_draw_a=round(cruise_current, 1),
            power_loading_w_kg=round(p_elec / mtow, 2),
            battery_c_rate=round(required_c_rate, 2),
        )

        # 9. Sizing Dynamic Performance (Max speed, Climb rates)
        # Solve level flight max power balance: V_max = V_cruise * (P_max / P_req)**0.33
        p_max_total = prop_count * max_avail_power_w
        max_speed = v_cruise * (p_max_total / max(1.0, p_elec)) ** 0.33
        max_speed_kmh = max_speed * 3.6

        # Climb rate = excess power / weight
        weight_n = mtow * 9.80665
        climb_factor = strategy.default_climb_power_factor
        avail_climb_power_w = p_max_total * eta_prop * eta_motor
        req_climb_power_w = p_mech * climb_factor
        excess_power = avail_climb_power_w - req_climb_power_w
        roc = excess_power / weight_n

        climb_angle = math.degrees(math.asin(max(0.01, min(0.9, roc / max(1.0, v_cruise)))))

        perf_analysis = CruisePerformanceAnalysis(
            max_speed_kmh=round(max_speed_kmh, 1),
            rate_of_climb_m_s=round(roc, 2),
            climb_angle_deg=round(climb_angle, 1),
            propulsive_efficiency=eta_prop,
            cruise_range_margin_km=15.0,
        )

        # 10. Coordinates Placements
        f_len = fuse_res.fuselage_geometry.length_m
        span = wing_res.wing_geometry.span_m

        placements: List[ForwardPlacement] = []
        if prop_count == 1:
            # Single Pusher: mounted on center rear firewall
            placements.append(ForwardPlacement(
                name="Center Rear Pusher",
                motor_model=motor["name"],
                propeller_model=propeller["name"],
                esc_model=esc["name"],
                x_m=round(-f_len * 0.5, 3),
                y_m=0.0,
                z_m=0.0,
                thrust_vector=[1.0, 0.0, 0.0],
            ))
        else:
            # Twin Tractor: mounted on wing nacelles spaced at 18% wingspan
            y_nacelle = span * 0.18
            placements.append(ForwardPlacement(
                name="Left Wing Tractor",
                motor_model=motor["name"],
                propeller_model=propeller["name"],
                esc_model=esc["name"],
                x_m=round(f_len * 0.35, 3),
                y_m=round(-y_nacelle, 3),
                z_m=0.05,
                thrust_vector=[1.0, 0.0, 0.0],
            ))
            placements.append(ForwardPlacement(
                name="Right Wing Tractor",
                motor_model=motor["name"],
                propeller_model=propeller["name"],
                esc_model=esc["name"],
                x_m=round(f_len * 0.35, 3),
                y_m=round(y_nacelle, 3),
                z_m=0.05,
                thrust_vector=[1.0, 0.0, 0.0],
            ))

        layout = ForwardPropulsionLayout(
            placements=placements,
            architecture=arch,
        )

        # 11. Compile Notes, warnings and recommendations
        notes = [
            f"Forward propulsion layout designed with {prop_count} propellers.",
            f"Selected cruise motor: {motor['name']} brushless motor (Kv: {motor['kv']:.0f}).",
            f"Selected ESC: {esc['name']} (Limit: {esc['current_limit_a']:.0f} A).",
        ]

        recs = strategy.get_recommendations()
        warnings: List[str] = []

        if roc < min(2.0, requirements.metadata.get("min_climb_rate", 1.5)):
            warnings.append("Low rate of climb reserve. Slower transition climb gradients expected.")

        result = ForwardPropulsionResult(
            motor_selection=motor,
            propeller_selection=propeller,
            esc_selection=esc,
            propulsion_layout=layout,
            cruise_analysis=analysis,
            power_analysis=power_analysis,
            performance_analysis=perf_analysis,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
            metadata={
                "strategy_applied": strategy.__class__.__name__,
            },
        )

        # 12. Run validation (raises error if invalid)
        self._validator.validate(requirements, result)

        meta = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        }
        result.metadata.update(meta)

        return result
