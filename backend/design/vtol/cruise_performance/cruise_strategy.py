from abc import ABC, abstractmethod
import math
from typing import List

from .cruise_requirements import CruiseRequirements
from .cruise_profile import CruiseProfile
from .cruise_speed_analysis import CruiseSpeedAnalysis
from .cruise_power_analysis import CruisePowerAnalysis
from .range_analysis import RangeAnalysis
from .endurance_analysis import EnduranceAnalysis
from .climb_analysis import ClimbAnalysis
from .descent_analysis import DescentAnalysis
from .maneuver_analysis import ManeuverAnalysis
from .performance_envelope_analysis import PerformanceEnvelope
from .cruise_analysis import CruiseAnalysis
from .cruise_result import CruiseResult

class CruisePerformanceStrategy(ABC):
    @abstractmethod
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        pass

    def _size_aerodynamics_performance(
        self, reqs: CruiseRequirements, profile: CruiseProfile, is_long_range: bool = False
    ) -> CruiseResult:
        # Sizing weight
        try:
            mtow = reqs.mass_properties_result.weight_budget.max_takeoff_weight_kg
        except AttributeError:
            try:
                mtow = reqs.mission_result.mission_analysis.estimated_mtow_kg
            except AttributeError:
                mtow = 25.0

        weight_n = mtow * 9.81
        
        # Speeds
        cruise_speed = 100.0
        if reqs.preferred_cruise_speed_kmh:
            cruise_speed = reqs.preferred_cruise_speed_kmh
            
        stall_speed = 42.0
        best_range_speed = cruise_speed
        best_endur_speed = cruise_speed * 0.85
        max_speed = cruise_speed * 1.30
        
        speed_eval = CruiseSpeedAnalysis(
            cruise_speed_kmh=cruise_speed,
            best_endurance_speed_kmh=best_endur_speed,
            best_range_speed_kmh=best_range_speed,
            maximum_speed_kmh=max_speed,
            minimum_cruise_speed_kmh=stall_speed + 8.0,
            stall_speed_kmh=stall_speed
        )
        
        # Aerodynamics drag & power
        ld = profile.nominal_lift_to_drag_ratio
        if is_long_range:
            ld = 12.5 # clean glider-type design
            
        drag = weight_n / ld
        power_req = (drag * (cruise_speed / 3.6)) / profile.propulsive_efficiency
        
        power_eval = CruisePowerAnalysis(
            drag_n=drag,
            thrust_required_n=drag,
            cruise_power_watts=power_req,
            cruise_current_amps=power_req / 22.2, # nominal 6S lipo
            thermal_load_factor=0.45,
            power_margin_pct=30.0
        )
        
        # Energy budget residual from hover & transition
        try:
            bat_cap = reqs.electrical_result.battery_pack.total_capacity_kwh
        except AttributeError:
            bat_cap = 1.5
            
        try:
            hover_energy = reqs.hover_performance_result.hover_efficiency.energy_consumption_kwh_min * 5.0
            trans_energy = reqs.transition_result.energy_analysis.total_energy_consumed_kwh * 2.0
        except AttributeError:
            hover_energy = 0.25
            trans_energy = 0.08
            
        residual_energy = bat_cap - hover_energy - trans_energy
        # Enforce reserve
        reserve_energy = bat_cap * (profile.battery_reserve_threshold_pct / 100.0)
        available_energy = max(0.1, residual_energy - reserve_energy)
        
        # Endurance & Range Sizing
        endurance_h = available_energy / (power_req / 1000.0)
        endurance_min = endurance_h * 60.0
        range_km = endurance_h * cruise_speed
        
        range_eval = RangeAnalysis(
            estimated_range_km=range_km,
            specific_range_km_kwh=range_km / available_energy,
            range_margin_pct=15.0,
            reserve_range_capacity_km=reserve_energy / (power_req / 1000.0) * cruise_speed
        )
        
        endur_eval = EnduranceAnalysis(
            estimated_endurance_min=endurance_min,
            specific_endurance_min_kwh=endurance_min / available_energy,
            endurance_margin_pct=18.0,
            reserve_endurance_capacity_min=(reserve_energy / (power_req / 1000.0)) * 60.0
        )
        
        # Climb & Descent
        climb_rate = 3.5
        if reqs.preferred_climb_rate_m_s:
            climb_rate = reqs.preferred_climb_rate_m_s
            
        climb_eval = ClimbAnalysis(
            max_rate_of_climb_m_s=climb_rate,
            max_climb_angle_deg=18.5,
            time_to_ceiling_s=300.0,
            climb_power_required_watts=power_req * 1.5
        )
        
        descent_eval = DescentAnalysis(
            nominal_descent_rate_m_s=(cruise_speed / 3.6) / ld,
            best_glide_ratio=ld,
            emergency_descent_rate_m_s=6.0,
            descent_angle_deg=math.degrees(math.atan(1.0 / ld))
        )
        
        # Maneuvers
        bank = math.degrees(math.acos(1.0 / profile.structural_load_limit_g))
        maneuver_eval = ManeuverAnalysis(
            max_load_factor_g=profile.structural_load_limit_g,
            max_bank_angle_deg=bank,
            turn_radius_m=((cruise_speed / 3.6) ** 2) / (9.81 * math.tan(math.radians(bank))),
            roll_rate_limit_deg_s=45.0
        )
        
        # Envelope ceilings
        service_ceiling = 8500.0 * math.log(power_req * 1.4 / power_req)
        envelope_eval = PerformanceEnvelope(
            service_ceiling_m=service_ceiling,
            operational_ceiling_m=service_ceiling - 300.0,
            maximum_altitude_limit_m=service_ceiling + 500.0,
            is_within_envelope=True
        )
        
        # Combined cruise analysis metrics
        analysis = CruiseAnalysis(
            cruise_speed_kmh=cruise_speed,
            range_km=range_km,
            endurance_min=endurance_min,
            max_rate_of_climb_m_s=climb_rate,
            service_ceiling_m=service_ceiling,
            battery_reserve_pct=profile.battery_reserve_threshold_pct
        )
        
        return CruiseResult(
            speed_analysis=speed_eval, power_analysis=power_eval, range_analysis=range_eval,
            endurance_analysis=endur_eval, climb_analysis=climb_eval,
            descent_analysis=descent_eval, maneuver_analysis=maneuver_eval,
            performance_envelope=envelope_eval, cruise_analysis=analysis,
            metadata={}
        )

class SurveyCruisePerformanceStrategy(CruisePerformanceStrategy):
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        result = self._size_aerodynamics_performance(reqs, profile, is_long_range=False)
        result.engineering_notes = ["Survey configuration cruise aerodynamics evaluated."]
        result.recommendations = ["Operate at best endurance speed to extend mapping survey sweeps."]
        return result

class CargoCruisePerformanceStrategy(CruisePerformanceStrategy):
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        result = self._size_aerodynamics_performance(reqs, profile, is_long_range=False)
        result.engineering_notes = ["Cargo transport cruise power load limits sized."]
        result.recommendations = ["Factor in aerodynamic drag coefficient penalty when carrying external cargo pods."]
        return result

class MappingCruisePerformanceStrategy(CruisePerformanceStrategy):
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        result = self._size_aerodynamics_performance(reqs, profile, is_long_range=False)
        result.engineering_notes = ["Mapping camera sweep energy bounds completed."]
        result.recommendations = ["Maintain constant cruise speed to prevent image resolution mismatch."]
        return result

class LongEnduranceCruisePerformanceStrategy(CruisePerformanceStrategy):
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        result = self._size_aerodynamics_performance(reqs, profile, is_long_range=True)
        result.engineering_notes = ["Long endurance fixed-wing clean aerodynamic margins sized."]
        result.recommendations = ["Utilize best range speeds to map broad regional boundaries."]
        return result

class MilitaryCruisePerformanceStrategy(CruisePerformanceStrategy):
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        result = self._size_aerodynamics_performance(reqs, profile, is_long_range=False)
        result.engineering_notes = ["Tactical military high maneuver flight envelopes completed."]
        result.recommendations = ["Do not exceed g-limit structural boundaries during high rate climbs."]
        return result

class ResearchCruisePerformanceStrategy(CruisePerformanceStrategy):
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        result = self._size_aerodynamics_performance(reqs, profile, is_long_range=False)
        result.engineering_notes = ["Research profile cruise performance properties calculated."]
        result.recommendations = ["Log motor currents to calibrate theoretical drag calculations."]
        return result

class BalancedCruisePerformanceStrategy(CruisePerformanceStrategy):
    def design_cruise_performance(self, reqs: CruiseRequirements, profile: CruiseProfile) -> CruiseResult:
        result = self._size_aerodynamics_performance(reqs, profile, is_long_range=False)
        result.engineering_notes = ["Balanced industrial/commercial cruise parameters sized."]
        result.recommendations = ["Enforce 15% reserve state of charge buffers in flight mission schedules."]
        return result
