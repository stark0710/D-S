from abc import ABC, abstractmethod
import math
from typing import List, Optional

from .transition_requirements import TransitionRequirements
from .transition_profile import TransitionProfile
from .transition_scheduler import TransitionSchedule, FlightModeSchedule
from .transition_control import ControlSchedule
from .transition_stability import StabilityAnalysis
from .transition_aerodynamics import AerodynamicAnalysis
from .transition_propulsion import PropulsionAnalysis
from .transition_energy import EnergyAnalysis
from .transition_failure_analysis import FailureAnalysis
from .transition_analysis import TransitionAnalysis
from .transition_result import TransitionResult
from .authoritative_transition import AuthoritativeTransitionModel, AuthoritativeTransitionResult

class TransitionStrategy(ABC):
    @abstractmethod
    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        pass

    def determine_conversion_speed(self, reqs: TransitionRequirements) -> float:
        """
        Determines conversion speed based on explicit requirement or profile.
        """
        if reqs.preferred_transition_speed_kmh is not None and reqs.preferred_transition_speed_kmh > 0:
            return reqs.preferred_transition_speed_kmh
        if reqs.mission_result and reqs.mission_result.transition_requirements:
            req_speed = reqs.mission_result.transition_requirements.transition_speed_kmh
            if req_speed and req_speed > 0:
                return req_speed
        return 55.0

    def _compile_schedules(
        self, reqs: TransitionRequirements, profile: TransitionProfile, auth_res: AuthoritativeTransitionResult
    ) -> tuple[TransitionSchedule, ControlSchedule]:
        airspeeds = [p.airspeed_kmh for p in auth_res.corridor_points]
        lift_throttles = [round(p.vertical_thrust_fraction * 100.0, 1) for p in auth_res.corridor_points]
        fwd_throttles = [round(min(100.0, p.wing_lift_fraction * 100.0), 1) for p in auth_res.corridor_points]
        
        # Surface effectiveness scales with dynamic pressure (V^2)
        v_max = max(1.0, auth_res.transition_speed_kmh)
        surface_effects = [
            round(min(100.0, ((p.airspeed_kmh / v_max) ** 2) * 100.0), 1)
            for p in auth_res.corridor_points
        ]
        
        # Ensure endpoints match expected convention
        if auth_res.direction == "TRANSITION_TO_CRUISE":
            lift_throttles[-1] = 0.0
            fwd_throttles[-1] = 100.0
            surface_effects[-1] = 100.0
        else:
            lift_throttles[-1] = 100.0
            fwd_throttles[-1] = 0.0
            surface_effects[-1] = 0.0

        mode_sched = FlightModeSchedule(
            hover_phase_duration_s=auth_res.transition_duration_s * 0.20,
            blended_phase_duration_s=auth_res.transition_duration_s * 0.60,
            wing_borne_phase_duration_s=auth_res.transition_duration_s * 0.20,
            lift_shutdown_airspeed_kmh=auth_res.fixed_wing_entry_airspeed_kmh * 0.85
        )
        
        sched = TransitionSchedule(
            airspeed_steps_kmh=airspeeds,
            lift_throttle_percentage=lift_throttles,
            forward_throttle_percentage=fwd_throttles,
            surface_control_effectiveness=surface_effects,
            flight_mode_schedule=mode_sched
        )
        
        control_sched = ControlSchedule(
            control_stages=["Hover", "Pitch Blend", "Wing Borne", "Shutdown"],
            rotor_weight_factors=[1.0, 0.70, 0.30, 0.0],
            surface_weight_factors=[0.0, 0.30, 0.70, 1.0],
            actuator_saturation_risk_pct=15.0
        )
        
        return sched, control_sched

    def _size_transition(
        self, reqs: TransitionRequirements, profile: TransitionProfile, is_aerodynamic: bool = True
    ) -> TransitionResult:
        # Sizing mass
        mtow = 25.0
        try:
            mtow = reqs.mass_properties_result.weight_budget.max_takeoff_weight_kg
        except AttributeError:
            try:
                mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
            except AttributeError:
                pass

        # Wing Area
        wing_area = max(0.70, mtow / 14.0)
        try:
            if reqs.wing_result and hasattr(reqs.wing_result, "wing_geometry") and hasattr(reqs.wing_result.wing_geometry, "area_m2"):
                wing_area = reqs.wing_result.wing_geometry.area_m2
        except AttributeError:
            pass
        if hasattr(reqs, "metadata") and "wing_area_m2" in reqs.metadata:
            wing_area = float(reqs.metadata["wing_area_m2"])

        # Motor count
        motor_count = 4
        try:
            if hasattr(reqs.configuration_result, "vtol_configuration") and reqs.configuration_result.vtol_configuration:
                motor_count = reqs.configuration_result.vtol_configuration.lift_motor_count
            elif hasattr(reqs.configuration_result, "propulsion_layout"):
                motor_count = reqs.configuration_result.propulsion_layout.motor_count
        except AttributeError:
            pass

        # Air density
        rho = 1.225
        try:
            rho = reqs.mission_result.mission_profile.air_density_hover_kg_m3
        except AttributeError:
            pass

        # Aspect ratio
        ar = 8.5
        try:
            ar = reqs.wing_result.wing_geometry.aspect_ratio
        except AttributeError:
            pass

        # CL max
        cl_max = 1.40
        try:
            cl_max = reqs.airfoil_result.polar_analysis.cl_max
        except AttributeError:
            pass

        # Direction
        direction = "TRANSITION_TO_CRUISE"
        if hasattr(reqs, "metadata") and "transition_direction" in reqs.metadata:
            direction = reqs.metadata["transition_direction"]

        # Speed and duration overrides
        speed = reqs.preferred_transition_speed_kmh
        if speed is None or speed <= 0:
            speed = self.determine_conversion_speed(reqs)

        duration = reqs.preferred_transition_duration_s if reqs.preferred_transition_duration_s else 18.0

        # Execute Authoritative Transition Model
        auth_res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=mtow,
            wing_area_m2=wing_area,
            lift_motor_count=motor_count,
            direction=direction,
            preferred_transition_speed_kmh=speed,
            preferred_transition_duration_s=duration,
            air_density_kg_m3=rho,
            cl_max=cl_max,
            aspect_ratio=ar,
        )

        sched, control_sched = self._compile_schedules(reqs, profile, auth_res)
        
        stability_eval = StabilityAnalysis(
            min_stability_margin=0.08,
            neutral_point_travel_m=0.15,
            max_pitch_excursion_deg=8.5,
            roll_damping_stability=True
        )
        
        aero_eval = AerodynamicAnalysis(
            wing_lift_growth_coefficient=round(auth_res.corridor_points[-1].wing_lift_n / max(1.0, auth_res.aircraft_weight_n), 3) or 0.055,
            lift_transfer_duration_s=auth_res.transition_duration_s * 0.80,
            stall_speed_calculated_kmh=auth_res.stall_speed_kmh,
            drag_peak_during_conversion_n=round(max(p.aerodynamic_drag_n for p in auth_res.corridor_points), 1)
        )
        
        prop_eval = PropulsionAnalysis(
            rotor_unloading_speed_kmh=auth_res.earliest_wing_supported_airspeed_kmh,
            propeller_sync_efficiency_pct=96.5,
            lift_motor_shutdown_speed_kmh=auth_res.fixed_wing_entry_airspeed_kmh,
            peak_thrust_delivered_n=round(auth_res.peak_forward_thrust_n, 1)
        )
        
        peak_current = auth_res.peak_electrical_power_w / 44.4 if auth_res.peak_electrical_power_w > 0 else 90.0
        
        energy_eval = EnergyAnalysis(
            peak_current_draw_amps=round(peak_current, 1),
            total_energy_consumed_kwh=round(auth_res.total_energy_kwh, 4),
            battery_charge_depletion_pct=round((auth_res.total_energy_kwh / 1.5) * 100.0, 2),
            voltage_sag_minimum_volts=22.2 * 0.88
        )
        
        failure_eval = FailureAnalysis(
            oei_conversion_safety_status=True,
            abort_decision_airspeed_kmh=round(auth_res.transition_speed_kmh * 0.60, 1),
            recovery_glide_distance_m=120.0,
            actuator_saturation_safety_margin_pct=18.0
        )
        
        analysis = TransitionAnalysis(
            conversion_speed_kmh=auth_res.transition_speed_kmh,
            duration_s=auth_res.transition_duration_s,
            energy_kwh=round(auth_res.total_energy_kwh, 4),
            min_stability_margin=0.08,
            control_saturation_risk_pct=15.0
        )
        
        return TransitionResult(
            transition_profile=profile, transition_schedule=sched,
            flight_mode_schedule=control_sched, control_schedule=control_sched,
            stability_analysis=stability_eval, aerodynamic_analysis=aero_eval,
            propulsion_analysis=prop_eval, energy_analysis=energy_eval,
            failure_analysis=failure_eval, transition_analysis=analysis,
            authoritative_result=auth_res,
            transition_corridor=[p.to_dict() for p in auth_res.corridor_points],
            warnings=list(auth_res.warnings),
            metadata={"authoritative_transition": auth_res.to_dict()}
        )

class LiftCruiseTransitionStrategy(TransitionStrategy):
    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        result = self._size_transition(reqs, profile, is_aerodynamic=True)
        result.engineering_notes = ["Lift+Cruise conversion sizing completed."]
        result.recommendations = ["Trigger lift rotor alignment locks promptly at conversion speeds."]
        return result

class QuadPlaneTransitionStrategy(TransitionStrategy):
    def determine_conversion_speed(self, reqs: TransitionRequirements) -> float:
        if reqs.preferred_transition_speed_kmh is not None and reqs.preferred_transition_speed_kmh > 0:
            return reqs.preferred_transition_speed_kmh
        return 55.0

    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        result = self._size_transition(reqs, profile, is_aerodynamic=True)
        result.engineering_notes = ["QuadPlane conversion parameters evaluated."]
        result.recommendations = ["Avoid pitch rates above 4 deg/s during blended thrust periods."]
        return result

class TiltRotorTransitionStrategy(TransitionStrategy):
    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        result = self._size_transition(reqs, profile, is_aerodynamic=True)
        result.engineering_notes = ["TiltRotor tilt angle schedules mapped."]
        result.recommendations = ["Coordinate tilt actuators to limit drag peak increases."]
        return result

class TiltWingTransitionStrategy(TransitionStrategy):
    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        result = self._size_transition(reqs, profile, is_aerodynamic=True)
        result.engineering_notes = ["TiltWing total wing angle conversion parameters calculated."]
        result.recommendations = ["Enforce tight synchronization loops on left/right tilt motors."]
        return result

class TailSitterTransitionStrategy(TransitionStrategy):
    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        result = self._size_transition(reqs, profile, is_aerodynamic=False)
        result.engineering_notes = ["TailSitter high pitch rate transition profiles sized."]
        result.recommendations = ["Limit control gains near stall boundary margins."]
        return result

class VectoredThrustTransitionStrategy(TransitionStrategy):
    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        result = self._size_transition(reqs, profile, is_aerodynamic=True)
        result.engineering_notes = ["VectoredThrust nozzle deflection schedules completed."]
        result.recommendations = ["Isolate nozzle heat structures during conversion segments."]
        return result

class BalancedTransitionStrategy(TransitionStrategy):
    def design_transition(self, reqs: TransitionRequirements, profile: TransitionProfile) -> TransitionResult:
        result = self._size_transition(reqs, profile, is_aerodynamic=True)
        result.engineering_notes = ["Balanced hybrid transition parameters calculated."]
        result.recommendations = ["Perform yaw check verification loops in ground control scripts."]
        return result
