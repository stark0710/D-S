from typing import Dict, List, Any
from backend.design.common.verification.models import VerificationRule

class RuleRegistry:
    def __init__(self):
        # Map configuration layout/type to list of rules
        # e.g., "Generic", "Fixed-Wing", "Multirotor", "VTOL"
        self._registry: Dict[str, List[VerificationRule]] = {
            "Generic": []
        }

    def register_rule(self, config_type: str, rule: VerificationRule):
        if config_type not in self._registry:
            self._registry[config_type] = []
        # Avoid duplicate rule_ids
        if any(r.rule_id == rule.rule_id for r in self._registry[config_type]):
            return
        self._registry[config_type].append(rule)

    def get_rules(self, config_type: str) -> List[VerificationRule]:
        rules = list(self._registry.get("Generic", []))
        if config_type != "Generic" and config_type in self._registry:
            rules.extend(self._registry[config_type])
        return rules

    def clear(self):
        self._registry = {
            "Generic": []
        }

# Global singleton rule registry instance
global_registry = RuleRegistry()
