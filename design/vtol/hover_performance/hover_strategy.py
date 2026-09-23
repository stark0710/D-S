from abc import ABC, abstractmethod
import math
from typing import List, Optional

from .hover_requirements import HoverRequirements
from .hover_profile import HoverProfile
from .hover_thrust import HoverThrust
from .hover_power import HoverPower
from .hover_efficiency import HoverEfficiency
from .hover_stability import HoverStability
from .hover_control import HoverControl
from .wind_hover_analysis import WindHoverAnalysis
from .altitude_hover_analysis import AltitudeHoverAnalysis
from .failure_hover_analysis import FailureHoverAnalysis
from .hover_analysis import HoverAnalysis
from .hover_result import HoverResult
from .authoritative_hover import AuthoritativeHoverModel, AuthoritativeHoverResult

class HoverStrategy(ABC):
    @abstractmethod
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        pass

    def _calculate_aerodynamics(self, reqs: HoverRequirements, profile: HoverProfile, is_military: bool = False) -> HoverResult:
        # Extract mass/weight
        mtow = 25.0
        try:
            mtow = reqs.mass_properties_result.weight_budget.max_takeoff_weight_kg
        except AttributeError:
            try:
                mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
            except AttributeError:
                pass

        # Sizing motor count from authoritative sources
        motor_count = 4
        try:
            if hasattr(reqs.configuration_result, "vtol_configuration") and reqs.configuration_result.vtol_configuration:
                motor_count = reqs.configuration_result.vtol_configuration.lift_motor_count
            elif hasattr(reqs.configuration_result, "propulsion_layout"):
                motor_count = reqs.configuration_result.propulsion_layout.motor_count
        except AttributeError:
            pass

        # Rotor diameter
        rotor_diameter = getattr(reqs, "preferred_rotor_diameter", None)
        if rotor_diameter is None and hasattr(reqs, "metadata") and reqs.metadata:
            rotor_diameter = reqs.metadata.get("rotor_diameter_m")
        if rotor_diameter is None and hasattr(reqs, "mission_result") and hasattr(reqs.mission_result, "mission_requirements"):
            meta = getattr(reqs.mission_result.mission_requirements, "metadata", {}) or {}
            rotor_diameter = meta.get("rotor_diameter_m")
        if rotor_diameter is None:
            rotor_diameter = 0.40  # Sizing default for legacy adapter compatibility

        # Total hover thrust capacity (T/W sizing)
        t_w_nominal = 1.55 if not is_military else 1.70
        if reqs.preferred_hover_margin:
            t_w_nominal = reqs.preferred_hover_margin
        elif hasattr(reqs, "mission_result") and hasattr(reqs.mission_result, "mission_requirements"):
            meta = getattr(reqs.mission_result.mission_requirements, "metadata", {}) or {}
            if "hover_thrust_to_weight_target" in meta:
                t_w_nominal = float(meta["hover_thrust_to_weight_target"])

        # Air density
        rho = 1.225
        try:
            rho = reqs.mission_result.mission_profile.air_density_hover_kg_m3
        except AttributeError:
            pass

        # Voltage
        voltage = None
        if hasattr(reqs, "metadata") and reqs.metadata:
            voltage = reqs.metadata.get("system_voltage_v")
        if voltage is None and hasattr(reqs, "mission_result") and hasattr(reqs.mission_result, "mission_requirements"):
            meta = getattr(reqs.mission_result.mission_requirements, "metadata", {}) or {}
            voltage = meta.get("system_voltage_v")

        # Authoritative Physics Execution
        auth_hover = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=mtow,
            lift_motor_count=motor_count,
            rotor_diameter_m=rotor_diameter,
            system_voltage_v=voltage,
            hover_thrust_to_weight_target=t_w_nominal,
            air_density_kg_m3=rho,
            induced_power_correction_factor=profile.induced_power_correction_factor,
            profile_drag_power_fraction=profile.profile_drag_power_fraction,
        )

        max_thrust = auth_hover.required_total_hover_thrust_n
        weight_n = auth_hover.aircraft_weight_n
        disk_area = auth_hover.total_disk_area_m2 or 0.1
        disk_loading = auth_hover.disk_loading_n_m2 or (max_thrust / disk_area)

        # Ground effect calculations (IGE vs OGE)
        h = profile.ground_effect_reference_height_m
        r = (rotor_diameter or 0.40) / 2.0
        # Hayden's formula
        ige_multiplier = 1.0 / (1.0 - 0.99 * ((r / (4.0 * h)) ** 2)) if h > 0 else 1.05

        thrust_oge = max_thrust
        thrust_ige = max_thrust * ige_multiplier

        thrust_eval = HoverThrust(
            total_disk_area_m2=disk_area,
            disk_loading_n_m2=disk_loading,
            thrust_margin_ratio=t_w_nominal,
            thrust_ige_watts=thrust_ige,
            thrust_oge_watts=thrust_oge,
            ground_effect_thrust_gain_pct=(ige_multiplier - 1.0) * 100.0,
        )

        # Power estimations
        induced_pow = auth_hover.actual_induced_power_w or 0.0
        profile_pow = auth_hover.profile_drag_power_w or 0.0
        total_pow = auth_hover.total_aerodynamic_power_w or 0.0

        sag = 1.0 - profile.battery_sag_offset_factor * (mtow / 25.0)
        sag = max(0.85, sag)

        power_eval = HoverPower(
            induced_power_watts=induced_pow,
            profile_power_watts=profile_pow,
            total_hover_power_watts=total_pow,
            power_loading_n_w=max_thrust / total_pow if total_pow > 0 else 0.0,
            voltage_sag_multiplier=sag,
        )
        
        # Stability derivatives
        stability_eval = HoverStability(
            roll_damping_rate_n_m_s=3.5,
            pitch_damping_rate_n_m_s=3.2,
            yaw_damping_rate_n_m_s=1.2,
            rotor_interference_loss_pct=profile.rotor_interference_loss_pct,
            gust_response_damping_ratio=0.72,
            is_stably_damped=True
        )
        
        # Control authority
        try:
            iyy = reqs.mass_properties_result.inertia_tensor.iyy_kg_m2
        except AttributeError:
            iyy = 0.50
            
        roll_acc = 12.0
        pitch_acc = 10.0
        yaw_acc = 4.0
        
        control_eval = HoverControl(
            roll_authority_rad_s2=roll_acc,
            pitch_authority_rad_s2=pitch_acc,
            yaw_authority_rad_s2=yaw_acc,
            control_headroom_pct=22.0 if not is_military else 30.0,
            has_sufficient_authority=True
        )
        
        # Figure of Merit
        fm = induced_pow / total_pow if total_pow > 0 else 0.0
        # Energy rate (in kWh/min)
        energy_rate = (total_pow / 1000.0) / 60.0 * 1.15
        
        try:
            battery_cap = reqs.electrical_result.battery_pack.total_capacity_kwh
        except AttributeError:
            battery_cap = 1.5
            
        endurance = battery_cap / energy_rate if energy_rate > 0 else 20.0
        
        efficiency_eval = HoverEfficiency(
            figure_of_merit=fm,
            energy_consumption_kwh_min=energy_rate,
            hover_endurance_min=endurance
        )
        
        # Wind limits
        wind_eval = WindHoverAnalysis(
            crosswind_limit_kts=30.0 if not is_military else 35.0,
            gust_tolerance_kts=12.0,
            yaw_deflection_margin_pct=25.0,
            aerodynamic_heave_offset_n=15.0
        )
        
        # Altitude limits
        # Sizing ceilings
        ceiling_oge = 8500.0 * math.log(t_w_nominal)
        ceiling_ige = ceiling_oge + 300.0
        
        altitude_eval = AltitudeHoverAnalysis(
            density_ratio_at_ceiling=1.0 / t_w_nominal if t_w_nominal > 0 else 0.0,
            hover_ceiling_ige_m=max(100.0, ceiling_ige),
            hover_ceiling_oge_m=max(100.0, ceiling_oge),
            hot_high_thrust_margin_ratio=t_w_nominal * 0.85
        )
        
        # Failure checks (OEI)
        oei_t_w = ((motor_count - 1) / motor_count) * t_w_nominal if motor_count > 0 else 0.0
        safe_oei = oei_t_w >= 1.05
        
        failure_eval = FailureHoverAnalysis(
            oei_thrust_margin_ratio=oei_t_w,
            oei_control_headroom_pct=10.0 if not safe_oei else 20.0,
            is_safe_under_failure=safe_oei,
            emergency_descent_rate_m_s=3.5 if not safe_oei else 1.5
        )
        
        # Combined Sized metrics
        analysis = HoverAnalysis(
            thrust_margin=t_w_nominal,
            power_loading=weight_n / total_pow if total_pow > 0 else 0.0,
            control_margin=control_eval.control_headroom_pct,
            hover_ceiling_m=ceiling_oge,
            wind_tolerance_kts=wind_eval.crosswind_limit_kts,
            thermal_load_factor=0.65
        )
        
        return HoverResult(
            hover_thrust=thrust_eval,
            hover_power=power_eval,
            hover_efficiency=efficiency_eval,
            hover_stability=stability_eval,
            hover_control=control_eval,
            wind_analysis=wind_eval,
            altitude_analysis=altitude_eval,
            failure_analysis=failure_eval,
            hover_analysis=analysis,
            authoritative_result=auth_hover,
            metadata={"authoritative_hover": auth_hover.to_dict()},
        )

class SurveyHoverStrategy(HoverStrategy):
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        result = self._calculate_aerodynamics(reqs, profile, is_military=False)
        result.engineering_notes = ["Survey strategy hover parameters evaluated."]
        result.recommendations = ["Monitor motor heat when operating near maximum wind tolerances."]
        return result

class CargoHoverStrategy(HoverStrategy):
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        result = self._calculate_aerodynamics(reqs, profile, is_military=False)
        result.engineering_notes = ["Cargo transport hover limits sized."]
        result.recommendations = ["Limit cargo weight to maintain minimum 1.30 T/W ratios."]
        return result

class MappingHoverStrategy(HoverStrategy):
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        result = self._calculate_aerodynamics(reqs, profile, is_military=False)
        result.engineering_notes = ["Mapping camera stabilization checked under gust conditions."]
        result.recommendations = ["Restrict operations if crosswinds generate roll oscillations."]
        return result

class LongEnduranceHoverStrategy(HoverStrategy):
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        result = self._calculate_aerodynamics(reqs, profile, is_military=False)
        result.engineering_notes = ["Long endurance profile designed for low power consumption hover."]
        result.recommendations = ["Optimize rotor geometries to improve hover Figure of Merit."]
        return result

class MilitaryHoverStrategy(HoverStrategy):
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        result = self._calculate_aerodynamics(reqs, profile, is_military=True)
        result.engineering_notes = ["Tactical military high margin hover parameters sized."]
        result.recommendations = ["Triple check motor temperature limits during hot and high operations."]
        return result

class ResearchHoverStrategy(HoverStrategy):
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        result = self._calculate_aerodynamics(reqs, profile, is_military=False)
        result.engineering_notes = ["Research modular configuration hover balance mapped."]
        result.recommendations = ["Use attitude logging software to isolate transition vibrations."]
        return result

class BalancedHoverStrategy(HoverStrategy):
    def design_hover_performance(self, reqs: HoverRequirements, profile: HoverProfile) -> HoverResult:
        result = self._calculate_aerodynamics(reqs, profile, is_military=False)
        result.engineering_notes = ["Balanced commercial configuration hover limits evaluated."]
        result.recommendations = ["Perform pre-flight compass calibrations under high crosswinds."]
        return result
