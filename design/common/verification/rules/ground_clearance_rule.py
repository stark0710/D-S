from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus

class GroundClearanceRule(VerificationRule):
    def __init__(self):
        super().__init__(
            rule_id="V_PROP_GROUND_CLEARANCE",
            title="Propeller Ground Clearance Compliance",
            description="Verifies that the propeller diameter is within the ground/fuselage clearance limit of the aircraft.",
            category=RuleCategory.GEOMETRY,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        prop_spec = context.subsystem_specifications.get("PropulsionSpecification")
        if not prop_spec:
            prop_spec = context.subsystem_specifications.get("PropulsionOptimizer")
            
        if not prop_spec:
            return RuleStatus.NOT_APPLICABLE, "No propulsion specification found.", ""

        prop_diam = 0.0
        if hasattr(prop_spec, "propeller_diameter_m"):
            prop_diam = getattr(prop_spec, "propeller_diameter_m", 0.0)
        elif hasattr(prop_spec, "propeller"):
            prop = getattr(prop_spec, "propeller")
            if isinstance(prop, dict):
                prop_diam = prop.get("diameter_m", 0.0)
            else:
                prop_diam = getattr(prop, "diameter_m", 0.0)

        fuse_spec = context.subsystem_specifications.get("FuselageSpecification")
        if not fuse_spec:
            fuse_spec = context.subsystem_specifications.get("FuselageOptimizer")

        fuse_height = 0.20
        if fuse_spec:
            fuse_height = getattr(fuse_spec, "height", 0.20)

        max_clearance = max(0.28, fuse_height * 2.0)

        if prop_diam > max_clearance + 1e-4:
            return (
                RuleStatus.FAIL,
                f"Propeller diameter ({prop_diam:.3f} m) exceeds maximum allowable clearance limit ({max_clearance:.3f} m).",
                "Select a propeller with smaller diameter or increase landing gear height."
            )
        return RuleStatus.PASS, f"Propeller diameter of {prop_diam:.3f} m satisfies ground clearance requirement.", ""
