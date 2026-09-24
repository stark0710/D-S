from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class MissionPerformanceRule(VerificationRule):
    """Verifies that the design performance meets mission range, endurance, and cruise speed targets."""

    def __init__(self):
        super().__init__(
            rule_id="V_MISSION_PERFORMANCE",
            title="Mission Performance Target Compliance",
            description="Verifies that the design cruise speed, range, and endurance satisfy the mission goals.",
            category=RuleCategory.MISSION,
            severity=RuleSeverity.ERROR
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        perf_spec = context.subsystem_specifications.get("FlightPerformanceSpecification")
        if not perf_spec:
            perf_spec = context.subsystem_specifications.get("FlightPerformanceOptimizer")
        if not perf_spec:
            return RuleStatus.NOT_APPLICABLE, "No flight performance specification found.", ""

        sized_range = getattr(perf_spec, "range_km", None) or 0.0
        sized_endurance = getattr(perf_spec, "endurance_min", None) or getattr(perf_spec, "estimated_flight_time_min", None) or 0.0
        sized_cruise = getattr(perf_spec, "cruise_speed_kmh", None) or 0.0

        req_range = 0.0
        req_endurance = 0.0
        req_cruise = 0.0

        reqs = context.mission_requirements
        if reqs:
            req_range = getattr(reqs, "target_range_km", 0.0)
            req_endurance = getattr(reqs, "target_flight_time_min", 0.0)
            req_cruise = getattr(reqs, "cruise_speed_kmh", 0.0)

            mr = getattr(reqs, "mission_result", None)
            if mr:
                constraints = getattr(mr, "constraints", None)
                if constraints:
                    if req_range == 0.0:
                        req_range = getattr(constraints, "minimum_range_km", None) or 0.0
                    if req_endurance == 0.0:
                        req_endurance = getattr(constraints, "minimum_endurance_min", None) or 0.0
                    if req_cruise == 0.0:
                        req_cruise = getattr(constraints, "target_cruise_speed_kmh", None) or 0.0
                if req_range == 0.0:
                    req_range = getattr(mr, "mission_range_km", None) or 0.0
                if req_endurance == 0.0:
                    req_endurance = (getattr(mr, "flight_time_min", None) or 0.0)
                if req_cruise == 0.0:
                    req_cruise = getattr(mr, "cruise_speed_kmh", None) or 0.0
            
            # Double fallback if endurance is still zero
            if req_endurance == 0.0:
                req_endurance = getattr(reqs, "flight_time_min", 0.0)

        failures = []
        if req_range > 0 and sized_range < req_range - 1e-4:
            failures.append(f"range ({sized_range:.1f} km vs required {req_range:.1f} km)")
        if req_endurance > 0 and sized_endurance < req_endurance - 1e-4:
            failures.append(f"endurance ({sized_endurance:.1f} min vs required {req_endurance:.1f} min)")
        if req_cruise > 0 and sized_cruise < req_cruise - 5.0:
            failures.append(f"cruise speed ({sized_cruise:.1f} km/h vs target {req_cruise:.1f} km/h)")

        if failures:
            msg = "Sized design falls short of performance targets: " + ", ".join(failures)
            return (
                RuleStatus.FAIL,
                msg,
                "Select a larger battery pack, a more efficient airfoil, or reduce overall drag profiles."
            )
        return RuleStatus.PASS, "All range, endurance, and cruise speed targets are satisfied.", ""
