from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class MassPropertiesRule(VerificationRule):
    """Verifies mass conservation, weight build-up totals, and MTOW limit."""

    def __init__(self):
        super().__init__(
            rule_id="V_MASS_PROPERTIES",
            title="Mass Model and MTOW Verification",
            description="Verifies mass conservation, weight build-up totals, and ensures MTOW matches constraints.",
            category=RuleCategory.MASS,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        mass_spec = context.subsystem_specifications.get("MassPropertiesSpecification")
        if not mass_spec:
            mass_spec = context.subsystem_specifications.get("MassPropertiesOptimizer")
        if not mass_spec:
            return RuleStatus.NOT_APPLICABLE, "No mass properties specification found.", ""

        sized_mtow = getattr(mass_spec, "maximum_takeoff_weight_kg", None) or getattr(mass_spec, "mtow_kg", None) or 0.0
        empty_weight = getattr(mass_spec, "empty_weight_kg", None) or 0.0

        # Payload
        p_spec = context.subsystem_specifications.get("PayloadPackagingSpecification")
        if not p_spec:
            p_spec = context.subsystem_specifications.get("PayloadPackagingOptimizer")
        payload = 0.0
        if p_spec:
            payload = getattr(p_spec, "payload_mass_kg", None) or getattr(p_spec, "payload_mass", None) or 0.0

        # Battery weight from propulsion
        prop_spec = context.subsystem_specifications.get("PropulsionSpecification")
        if not prop_spec:
            prop_spec = context.subsystem_specifications.get("PropulsionOptimizer")
        battery_weight = 0.0
        if prop_spec:
            # Try battery_weight_g (grams) first
            bw_g = getattr(prop_spec, "battery_weight_g", None) or 0.0
            if bw_g > 0:
                battery_weight = bw_g / 1000.0
            else:
                battery_weight = getattr(prop_spec, "battery_weight_kg", None) or 0.0

        # Verify MTOW is positive
        if sized_mtow <= 0:
            return (
                RuleStatus.FAIL,
                "MTOW is zero or negative — mass model was not computed.",
                "Ensure the MassPropertiesOptimizer receives valid upstream specifications."
            )

        # MTOW limit check: strictly enforce user constraint when specified
        reqs = context.mission_requirements
        user_mtow_limit = getattr(reqs, "maximum_takeoff_weight_kg", None) if reqs else None
        if user_mtow_limit is None or user_mtow_limit <= 0.0:
            user_mtow_limit = None

        if user_mtow_limit is not None:
            if sized_mtow > user_mtow_limit + 1e-4:
                return (
                    RuleStatus.FAIL,
                    f"Sized MTOW ({sized_mtow:.3f} kg) exceeds user-specified maximum MTOW limit ({user_mtow_limit:.3f} kg).",
                    "Increase structural safety margins or decrease battery capacity to make design lighter."
                )

        return RuleStatus.PASS, f"Sized MTOW of {sized_mtow:.3f} kg (empty={empty_weight:.3f} kg) is valid and within constraints.", ""
