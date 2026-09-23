"""
ConstraintRegistry Subsystem

Purpose:
    Defines the `ConstraintRegistry` class responsible for registering and managing engineering constraint rules.

Role in Architecture:
    `ConstraintRegistry` provides the plugin registry for constraint validation rules.
    It enables dynamic registration of new aircraft-specific or domain-specific constraint rules.
"""

from backend.design.components.constraints.constraint_rule import ConstraintRule


class ConstraintRegistry:
    """
    Registry for managing engineering constraint validation rules.

    Design Principles:
        - Registry Pattern: Centralized rule registration.
        - Open/Closed Principle: Extensible plugin architecture for future constraint rules.
    """

    def __init__(self) -> None:
        """Initializes the ConstraintRegistry."""
        self._rules: list[ConstraintRule] = []

    def register_rule(self, rule: ConstraintRule) -> None:
        """
        Registers a new constraint rule.

        Args:
            rule (ConstraintRule): Constraint rule instance to register.
        """
        for existing in self._rules:
            if existing.rule_name == rule.rule_name:
                return  # Skip duplicate registration
        self._rules.append(rule)

    def registered_rules(self) -> list[ConstraintRule]:
        """Returns a list of all registered ConstraintRule instances."""
        return list(self._rules)
