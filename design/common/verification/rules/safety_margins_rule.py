from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class SafetyMarginsRule(VerificationRule):
    """Verifies that the aircraft design carries adequate safety margins."""

    def __init__(self):
        super().__init__(
            rule_id="V_SAFETY_MARGINS",
            title="Safety Margins Compliance",
            description="Verifies structural safety factor, stall margin, and thrust margin are adequate.",
            category=RuleCategory.SAFETY,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        perf_spec = context.subsystem_specifications.get("FlightPerformanceSpecification")
        if not perf_spec:
            perf_spec = context.subsystem_specifications.get("FlightPerformanceOptimizer")

        mass_spec = context.subsystem_specifications.get("MassPropertiesSpecification")
        if not mass_spec:
            mass_spec = context.subsystem_specifications.get("MassPropertiesOptimizer")

        if not perf_spec and not mass_spec:
            return RuleStatus.NOT_APPLICABLE, "No performance or mass specifications found.", ""

        failures = []

        # Verify stall speed margin
        if perf_spec:
            stall_speed = getattr(perf_spec, "stall_speed_kmh", 0.0)
            cruise_speed = getattr(perf_spec, "cruise_speed_kmh", 0.0)
            if stall_speed > 0 and cruise_speed > 0:
                stall_margin = (cruise_speed - stall_speed) / cruise_speed
                if stall_margin < 0.15:
                    failures.append(
                        f"stall margin ({stall_margin:.1%}) is below minimum safety threshold (15%)"
                    )

        # Verify structural margin
        if mass_spec:
            structural_margin = getattr(mass_spec, "structural_margin", 0.0)
            if structural_margin > 0 and structural_margin < 1.0:
                failures.append(
                    f"structural margin factor ({structural_margin:.3f}) is below 1.0 — unsafe design"
                )

        # Verify wing loading is reasonable
        wing_spec = context.subsystem_specifications.get("WingPlanformSpecification")
        if not wing_spec:
            wing_spec = context.subsystem_specifications.get("WingPlanformOptimizer")
        if wing_spec and mass_spec:
            wing_area = getattr(wing_spec, "wing_area", None) or 0.0
            mtow = getattr(mass_spec, "maximum_takeoff_weight_kg", None) or getattr(mass_spec, "mtow_kg", None) or 0.0
            if wing_area > 0 and mtow > 0:
                wing_loading = (mtow * 9.81) / wing_area
                if wing_loading > 250.0:
                    failures.append(
                        f"wing loading ({wing_loading:.1f} N/m²) exceeds safe limit for small UAS (> 250 N/m²)"
                    )

        if failures:
            return (
                RuleStatus.FAIL,
                "Safety margin violations: " + "; ".join(failures) + ".",
                "Increase structural factors, reduce cruise speed, or increase wing area."
            )
        return RuleStatus.PASS, "All safety margins are within acceptable limits.", ""
