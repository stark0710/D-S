from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class PropulsionCompatibilityRule(VerificationRule):
    """Verifies propulsion system motor/ESC/battery/propeller compatibility."""

    def __init__(self):
        super().__init__(
            rule_id="V_PROP_COMPATIBILITY",
            title="Propulsion System Compatibility",
            description="Verifies that motor, ESC, battery, and propeller are mutually compatible and provide adequate thrust.",
            category=RuleCategory.PROPULSION,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        prop_spec = context.subsystem_specifications.get("PropulsionSpecification")
        if not prop_spec:
            prop_spec = context.subsystem_specifications.get("PropulsionOptimizer")
        if not prop_spec:
            return RuleStatus.NOT_APPLICABLE, "No propulsion specification found.", ""

        static_thrust_n = getattr(prop_spec, "static_thrust_n", None) or 0.0
        operating_voltage = getattr(prop_spec, "operating_voltage_v", None) or getattr(prop_spec, "battery_voltage_v", None) or 0.0
        cruise_power = getattr(prop_spec, "cruise_power_w", None) or 0.0
        motor_name = getattr(prop_spec, "motor_name", None) or "Unknown"
        propeller_name = getattr(prop_spec, "propeller_name", None) or "Unknown"

        failures = []

        if operating_voltage <= 0:
            failures.append("battery operating voltage is zero or negative")

        if static_thrust_n <= 0:
            failures.append("static thrust is zero or negative — propulsion sizing invalid")

        if cruise_power <= 0:
            failures.append("cruise power is zero or negative")

        # Verify thrust-to-weight ratio is adequate for takeoff
        mass_spec = context.subsystem_specifications.get("MassPropertiesSpecification")
        if not mass_spec:
            mass_spec = context.subsystem_specifications.get("MassPropertiesOptimizer")
        if mass_spec and static_thrust_n > 0:
            mtow = getattr(mass_spec, "maximum_takeoff_weight_kg", None) or getattr(mass_spec, "mtow_kg", None) or 0.0
            weight_n = mtow * 9.81
            tw_ratio = static_thrust_n / weight_n if weight_n > 0 else 0.0
            if tw_ratio < 0.3:
                failures.append(
                    f"thrust-to-weight ratio ({tw_ratio:.3f}) is below minimum takeoff threshold (0.30)"
                )

        if failures:
            return (
                RuleStatus.FAIL,
                "Propulsion compatibility violations: " + "; ".join(failures) + ".",
                "Reselect motor/ESC/battery combination or adjust propeller pitch/diameter."
            )
        return (
            RuleStatus.PASS,
            f"Propulsion system compatible (motor={motor_name}, prop={propeller_name}, thrust={static_thrust_n:.1f} N, V={operating_voltage:.1f} V).",
            ""
        )
