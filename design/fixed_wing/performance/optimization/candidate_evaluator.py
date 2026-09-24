"""
Fixed-Wing Flight Performance Candidate Evaluator
"""

from typing import List, Dict, Any
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
from backend.design.fixed_wing.mass_properties.mass_result import MassResult
from backend.design.fixed_wing.mass_properties.weight_breakdown import WeightBreakdown
from backend.design.fixed_wing.mass_properties.mass_analysis import MassAnalysis
from backend.design.fixed_wing.flight_performance.flight_performance_engine import FlightPerformanceEngine
from backend.design.fixed_wing.flight_performance.flight_profile import FlightProfile


class DummyObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class CGCandidateEvaluator:
    """Dummy class to provide clean interface compatibility if needed."""
    pass


class FlightPerformanceCandidateEvaluator:
    """
    Candidate evaluator that wraps preceding specification data into unified FlightRequirements
    and calls the FlightPerformanceEngine backend to run performance assessments.
    """
    def __init__(self) -> None:
        self.perf_engine = FlightPerformanceEngine()

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        # Retrieve preceding specification outputs
        wing_spec = context.previous_specifications.get("WingPlanformOptimizer") or context.previous_specifications.get("WingPlanformSpecification")
        fuse_spec = context.previous_specifications.get("FuselageOptimizer") or context.previous_specifications.get("FuselageSpecification")
        tail_spec = context.previous_specifications.get("TailOptimizer") or context.previous_specifications.get("TailSpecification")
        prop_spec = context.previous_specifications.get("PropulsionOptimizer") or context.previous_specifications.get("PropulsionSpecification")
        elec_spec = context.previous_specifications.get("ElectricalOptimizer") or context.previous_specifications.get("ElectricalSystemSpecification")
        mass_spec = context.previous_specifications.get("MassPropertiesOptimizer") or context.previous_specifications.get("MassPropertiesSpecification")
        cg_spec = context.previous_specifications.get("CGOptimizer") or context.previous_specifications.get("CGSpecification")

        # Fallback values for mass components
        if mass_spec:
            breakdown = mass_spec.weight_breakdown
            mtow = getattr(mass_spec, "maximum_takeoff_weight_kg", 8.5) or getattr(mass_spec, "mtow_kg", 8.5)
        else:
            breakdown = {
                "wing": 1.344, "fuselage": 1.89, "horizontal_tail": 0.176, "vertical_tail": 0.132,
                "landing_gear": 0.35, "motor": 0.310, "propeller": 0.065, "esc": 0.080,
                "battery": 1.200, "flight_controller": 0.080,
                "gps": 0.050, "receiver": 0.010, "telemetry": 0.030,
                "power_module": 0.025, "bec": 0.015, "servos": 0.112,
                "mission_equipment": 0.500, "payload": 1.5,
                "fasteners": 0.05, "wiring": 0.120, "paint_finish": 0.02,
                "safety_margin": 0.3,
            }
            mtow = sum(breakdown.values())

        # Build WeightBreakdown
        if isinstance(breakdown, dict):
            struct_w = sum(breakdown[w] for w in ["wing", "fuselage", "horizontal_tail", "vertical_tail", "landing_gear"] if w in breakdown)
            prop_w = sum(breakdown[p] for p in ["motor", "propeller", "esc"] if p in breakdown)
            av_w = sum(breakdown[a] for a in ["flight_controller", "gps", "receiver", "telemetry", "power_module", "bec", "servos"] if a in breakdown)
            pay_w = breakdown.get("payload", 1.5)
            batt_w = breakdown.get("battery", 1.2)
        else:
            struct_w = breakdown.structural_weight_kg
            prop_w = breakdown.propulsion_weight_kg
            av_w = breakdown.avionics_weight_kg
            pay_w = breakdown.payload_weight_kg
            batt_w = breakdown.battery_fuel_weight_kg

        mass_breakdown = WeightBreakdown(
            structural_weight_kg=round(struct_w, 3),
            propulsion_weight_kg=round(prop_w, 3),
            avionics_weight_kg=round(av_w, 3),
            payload_weight_kg=round(pay_w, 3),
            battery_fuel_weight_kg=round(batt_w, 3),
            useful_load_kg=round(pay_w + batt_w, 3),
            payload_fraction=round(pay_w / mtow, 3),
            battery_fraction=round(batt_w / mtow, 3),
        )

        # Build MassResult
        static_m = getattr(cg_spec, "static_margin", 0.15) if cg_spec else 0.15
        mass_res = MassResult(
            weight_breakdown=mass_breakdown,
            component_masses=[],
            center_of_gravity=getattr(cg_spec, "cg_position", (0.5, 0.0, 0.0)) if cg_spec else (0.5, 0.0, 0.0),
            moments_of_inertia=getattr(mass_spec, "moments_of_inertia", (0.02, 0.45, 0.43)) if mass_spec else (0.02, 0.45, 0.43),
            loading_conditions=[],
            static_margin=static_m,
            mass_analysis=MassAnalysis(90.0, 90.0, 95.0, 1.5, 0.40, "Feasible weight build-up"),
        )

        # Build dynamic wrappers
        prop_res = PropulsionResultWrapper(prop_spec, mtow)
        av_res = AvionicsResultWrapper(elec_spec)
        pay_res = PayloadResultWrapper()

        # Construct FlightRequirements
        reqs = FlightRequirements(
            mission_result=context.requirements.mission_result,
            configuration_result=context.requirements.configuration_result,
            wing_result=context.requirements.wing_result,
            airfoil_result=context.requirements.airfoil_result,
            tail_result=context.requirements.tail_result,
            fuselage_result=context.requirements.fuselage_result,
            propulsion_result=prop_res,
            avionics_result=av_res,
            payload_result=pay_res,
            mass_result=mass_res,
            electrical_result=elec_spec,
        )

        # Run PerformanceEngine Sizer calculations
        prof = FlightProfile()
        try:
            result = self.perf_engine.process_performance_design(reqs, prof)
            failed_validation = False
            validation_error_msg = ""
        except Exception as e:
            failed_validation = True
            validation_error_msg = str(e)
            result = None

        candidate.derived_variables["failed_validation"] = failed_validation
        candidate.derived_variables["validation_error_msg"] = validation_error_msg

        if not failed_validation and result is not None:
            # Save to derived variables
            candidate.derived_variables["flight_result"] = result
            candidate.derived_variables["stall_speed"] = result.stall_analysis.stall_speed_clean_kmh
            candidate.derived_variables["cruise_speed"] = result.cruise_analysis.cruise_speed_kmh
            candidate.derived_variables["maximum_speed"] = result.performance_analysis.maximum_speed_kmh
            candidate.derived_variables["takeoff_distance"] = result.takeoff_analysis.takeoff_distance_m
            candidate.derived_variables["landing_distance"] = result.landing_analysis.landing_distance_m
            candidate.derived_variables["rate_of_climb"] = result.climb_analysis.rate_of_climb_m_s
            candidate.derived_variables["range"] = result.range_analysis.maximum_range_km
            candidate.derived_variables["endurance"] = result.endurance_analysis.maximum_endurance_min
            candidate.derived_variables["power_required"] = result.cruise_analysis.power_required_w
            candidate.derived_variables["power_available"] = prop_res.power_analysis.maximum_power_w
            candidate.derived_variables["energy_consumption"] = result.range_analysis.energy_consumption_rate_wh_km
            candidate.derived_variables["mission_margin"] = result.mission_performance.energy_margin_pct
        else:
            # Fallback values
            candidate.derived_variables["flight_result"] = None
            candidate.derived_variables["stall_speed"] = 999.0
            candidate.derived_variables["cruise_speed"] = 0.0
            candidate.derived_variables["maximum_speed"] = 0.0
            candidate.derived_variables["takeoff_distance"] = 999.0
            candidate.derived_variables["landing_distance"] = 999.0
            candidate.derived_variables["rate_of_climb"] = -999.0
            candidate.derived_variables["range"] = 0.0
            candidate.derived_variables["endurance"] = 0.0
            candidate.derived_variables["power_required"] = 9999.0
            candidate.derived_variables["power_available"] = prop_res.power_analysis.maximum_power_w
            candidate.derived_variables["energy_consumption"] = 9999.0
            candidate.derived_variables["mission_margin"] = -100.0


class PropulsionResultWrapper:
    def __init__(self, spec, mtow):
        self.spec = spec
        cap_mah = getattr(spec, "battery_capacity_mah", 0.0) if spec else 0.0
        v_nom = getattr(spec, "operating_voltage_v", 0.0) if spec else 0.0
        self.battery_energy_wh = (cap_mah / 1000.0) * v_nom if cap_mah > 0 and v_nom > 0 else None
        self.power_analysis = DummyObject(
            maximum_power_w=getattr(spec, "takeoff_power_w", 500.0) if spec else 500.0,
            required_cruise_power_w=getattr(spec, "cruise_power_w", 150.0) if spec else 150.0
        )
        self.efficiency_analysis = DummyObject(
            propeller_efficiency=getattr(spec, "propeller_efficiency", 0.75) if spec else 0.75,
            total_system_efficiency=getattr(spec, "total_efficiency", 0.60) if spec else 0.60
        )
        static_t = getattr(spec, "static_thrust_n", 50.0) if spec else 50.0
        self.thrust_analysis = DummyObject(
            thrust_to_weight_ratio=round(static_t / (max(0.1, mtow) * 9.81), 3)
        )
        self.cruise_analysis = DummyObject(
            throttle_setting_pct=50.0
        )


class AvionicsResultWrapper:
    def __init__(self, elec_spec):
        self.power_analysis = DummyObject(
            continuous_power_w=getattr(elec_spec, "electrical_power_budget_w", 15.0) if elec_spec else 15.0
        )


class PayloadResultWrapper:
    def __init__(self):
        self.payload_analysis = DummyObject(
            power_consumption_w=5.0
        )
