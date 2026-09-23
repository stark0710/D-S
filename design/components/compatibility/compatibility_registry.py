"""
CompatibilityRegistry Subsystem

Purpose:
    Defines the `CompatibilityRegistry` class responsible for registering and managing compatibility rules.

Role in Architecture:
    `CompatibilityRegistry` provides the plugin registry for compatibility rules.
    It enables dynamic registration of new engineering compatibility rules without modifying core engine logic.
"""

from backend.design.components.compatibility.compatibility_rule import CompatibilityRule


class CompatibilityRegistry:
    """
    Registry for managing compatibility validation rules.

    Design Principles:
        - Registry Pattern: Centralized rule registration.
        - Open/Closed Principle: Extensible plugin architecture for future compatibility rules.
    """

    def __init__(self) -> None:
        """Initializes the CompatibilityRegistry."""
        self._rules: list[CompatibilityRule] = []

    def register_rule(self, rule: CompatibilityRule) -> None:
        """
        Registers a new compatibility rule.

        Args:
            rule (CompatibilityRule): Compatibility rule instance to register.
        """
        for existing in self._rules:
            if existing.rule_name == rule.rule_name:
                return  # Skip duplicate registration
        self._rules.append(rule)

    def registered_rules(self) -> list[CompatibilityRule]:
        """Returns a list of all registered CompatibilityRule instances."""
        return list(self._rules)
