"""
ScoringRegistry Subsystem

Purpose:
    Defines the `ScoringRegistry` class responsible for registering and managing quantitative category scoring rules.

Role in Architecture:
    `ScoringRegistry` provides the plugin registry for category scoring rules.
    It enables dynamic registration of new category scoring rules without modifying core engine logic.
"""

from backend.design.components.scoring.scoring_rule import ScoringRule


class ScoringRegistry:
    """
    Registry for managing quantitative category scoring rules.

    Design Principles:
        - Registry Pattern: Centralized rule registration.
        - Open/Closed Principle: Extensible plugin architecture for future scoring rules.
    """

    def __init__(self) -> None:
        """Initializes the ScoringRegistry."""
        self._rules: list[ScoringRule] = []

    def register_rule(self, rule: ScoringRule) -> None:
        """
        Registers a new scoring rule.

        Args:
            rule (ScoringRule): Scoring rule instance to register.
        """
        for existing in self._rules:
            if existing.rule_name == rule.rule_name:
                return  # Skip duplicate registration
        self._rules.append(rule)

    def registered_rules(self) -> list[ScoringRule]:
        """Returns a list of all registered ScoringRule instances."""
        return list(self._rules)
