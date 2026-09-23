"""
RuleRepository Subsystem

Purpose:
    Defines the `RuleRepository` class, which serves as the canonical in-memory storage,
    indexing, and lookup engine for all loaded `EngineeringRule` objects.

Role in Architecture:
    `RuleRepository` acts as the single source of truth for engineering rules and constraints within the backend.
    Future subsystems (RuleEngine, ConstraintEngine, CompatibilityEngine, DesignEngine, and OptimizationEngine)
    query `RuleRepository` to retrieve rules by ID, subsystem category, or severity level.
"""

from collections import defaultdict
from backend.rules.models.engineering_rule import EngineeringRule, RuleSeverity


class RuleRepositoryError(ValueError):
    """Base exception class for RuleRepository operations."""
    pass


class DuplicateRuleIDError(RuleRepositoryError):
    """Raised when multiple engineering rules with the same ID are added to the repository."""
    pass


class RuleNotFoundError(RuleRepositoryError, KeyError):
    """Raised when looking up a rule ID that does not exist in the repository."""
    pass


class RuleRepository:
    """
    In-memory canonical storage layer and index for EngineeringRule objects.

    Maintains:
        - `_rules`: list[EngineeringRule]
        - `_rule_id_index`: dict[str, EngineeringRule]
        - `_category_index`: dict[str, list[EngineeringRule]]
        - `_severity_index`: dict[RuleSeverity, list[EngineeringRule]]

    Design Principles:
        - Single Responsibility Principle (SRP): Stores, indexes, and exposes engineering rules.
        - Immutable Indexing: Read-only lookup operations after initialization.
        - Clean Architecture: Completely decoupled from evaluation logic and expression parsing.
    """

    def __init__(self, rules: list[EngineeringRule] | None = None) -> None:
        """
        Initializes the RuleRepository and populates internal indexes.

        Args:
            rules (list[EngineeringRule] | None): Initial list of loaded engineering rules.

        Raises:
            DuplicateRuleIDError: If duplicate rule IDs are detected.
        """
        self._rules: list[EngineeringRule] = list(rules) if rules else []
        self._rule_id_index: dict[str, EngineeringRule] = {}
        self._category_index: dict[str, list[EngineeringRule]] = defaultdict(list)
        self._severity_index: dict[RuleSeverity, list[EngineeringRule]] = defaultdict(list)

        self._build_indexes()

    def _build_indexes(self) -> None:
        """Populates ID, category, and severity lookup indexes while enforcing unique rule IDs."""
        self._rule_id_index.clear()
        self._category_index.clear()
        self._severity_index.clear()

        for rule in self._rules:
            # Enforce unique rule ID constraint
            if rule.id in self._rule_id_index:
                existing = self._rule_id_index[rule.id]
                raise DuplicateRuleIDError(
                    f"Duplicate rule ID detected: '{rule.id}' is shared by '{existing.name}' and '{rule.name}'."
                )

            self._rule_id_index[rule.id] = rule

            # Index by category
            category_key = rule.category.strip().lower()
            self._category_index[category_key].append(rule)

            # Index by severity
            self._severity_index[rule.severity].append(rule)

    def get_all(self) -> list[EngineeringRule]:
        """
        Returns all stored EngineeringRule objects.

        Returns:
            list[EngineeringRule]: List of all rules in the repository.
        """
        return list(self._rules)

    def get_rule(self, rule_id: str) -> EngineeringRule:
        """
        Retrieves a single EngineeringRule by its unique string ID in O(1) time.

        Args:
            rule_id (str): Unique rule identifier.

        Returns:
            EngineeringRule: Matching engineering rule object.

        Raises:
            RuleNotFoundError: If no rule with rule_id exists.
        """
        if rule_id not in self._rule_id_index:
            raise RuleNotFoundError(
                f"Rule with ID '{rule_id}' not found in RuleRepository."
            )
        return self._rule_id_index[rule_id]

    def has_rule(self, rule_id: str) -> bool:
        """
        Checks whether a rule with the specified ID exists in the repository.

        Args:
            rule_id (str): Unique rule identifier.

        Returns:
            bool: True if the rule exists; False otherwise.
        """
        return rule_id in self._rule_id_index

    def get_by_category(self, category: str) -> list[EngineeringRule]:
        """
        Retrieves all EngineeringRules belonging to the specified category string.

        Args:
            category (str): Subsystem or domain category string (e.g., 'Electrical', 'Aerodynamics').

        Returns:
            list[EngineeringRule]: List of matching rules, or empty list if none exist.
        """
        category_key = (category or "").strip().lower()
        return list(self._category_index.get(category_key, []))

    def get_by_severity(self, severity: RuleSeverity | str) -> list[EngineeringRule]:
        """
        Retrieves all EngineeringRules matching the specified severity level.

        Args:
            severity (RuleSeverity | str): Severity enum member or string value (e.g., RuleSeverity.CRITICAL, "CRITICAL").

        Returns:
            list[EngineeringRule]: List of matching rules, or empty list if none exist.
        """
        if isinstance(severity, str):
            try:
                severity_enum = RuleSeverity(severity.upper())
            except ValueError:
                return []
        else:
            severity_enum = severity

        return list(self._severity_index.get(severity_enum, []))

    def categories(self) -> list[str]:
        """
        Returns a sorted list of all distinct category names currently stored in the repository.

        Returns:
            list[str]: Sorted list of original category names.
        """
        distinct_categories: set[str] = {rule.category for rule in self._rules}
        return sorted(distinct_categories)

    def count(self) -> int:
        """
        Returns total number of stored engineering rules.

        Returns:
            int: Number of rules in the repository.
        """
        return len(self._rules)
