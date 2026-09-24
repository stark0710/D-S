from typing import Tuple, Any
from backend.design.common.verification.models import VerificationRule, RuleCategory, RuleSeverity, RuleStatus


class MissionPayloadRule(VerificationRule):
    """Verifies that the synthesized aircraft can carry the required mission payload."""

    def __init__(self):
        super().__init__(
            rule_id="V_MISSION_PAYLOAD",
            title="Mission Payload Requirement Compliance",
            description="Verifies that the synthesized aircraft design can carry the required mission payload mass.",
            category=RuleCategory.MISSION,
            severity=RuleSeverity.CRITICAL
        )
        self.config_type = "Generic"

    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        sized_payload = 0.0
        
        # Try MassPropertiesSpecification subsystem_masses['payload']
        mass_spec = context.subsystem_specifications.get("MassPropertiesSpecification")
        if not mass_spec:
            mass_spec = context.subsystem_specifications.get("MassPropertiesOptimizer")
        if mass_spec:
            subsystem_masses = getattr(mass_spec, "subsystem_masses", None)
            if isinstance(subsystem_masses, dict):
                sized_payload = subsystem_masses.get("payload", 0.0)

        # Fallback to PayloadPackagingSpecification if needed
        if sized_payload == 0.0:
            p_spec = context.subsystem_specifications.get("PayloadPackagingSpecification")
            if not p_spec:
                p_spec = context.subsystem_specifications.get("PayloadPackagingOptimizer")
            if p_spec:
                sized_payload = getattr(p_spec, "payload_mass_kg", None) or getattr(p_spec, "payload_mass", None) or 0.0

        req_payload = 0.0
        reqs = context.mission_requirements
        if reqs:
            req_payload = getattr(reqs, "payload_weight_kg", 0.0)
            if req_payload == 0.0:
                req_payload = getattr(reqs, "payload_kg", 0.0)
            mr = getattr(reqs, "mission_result", None)
            if mr:
                constraints = getattr(mr, "constraints", None)
                if constraints:
                    if req_payload == 0.0:
                        req_payload = getattr(constraints, "minimum_payload_kg", None) or 0.0
                if req_payload == 0.0:
                    req_payload = getattr(mr, "payload_kg", None) or 0.0

        if sized_payload < req_payload - 1e-4:
            return (
                RuleStatus.FAIL,
                f"Sized payload capacity ({sized_payload:.3f} kg) is below the required payload mass ({req_payload:.3f} kg).",
                "Re-examine the payload packaging constraint bounds or check if structural mass is too high."
            )
        return RuleStatus.PASS, f"Sized payload capacity ({sized_payload:.3f} kg) satisfies the mission requirements ({req_payload:.3f} kg).", ""
