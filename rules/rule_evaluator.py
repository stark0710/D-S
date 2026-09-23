"""
RuleEvaluator Single-Rule Evaluation Subsystem

Purpose:
    Defines the `RuleEvaluator` class responsible for evaluating a single `EngineeringRule` against a design context dictionary.

Role in Architecture:
    `RuleEvaluator` serves as the core rule evaluation engine for Phase 4 (Engineering Rules Platform).
    It parses declarative comparison condition expressions (supporting ==, !=, <, <=, >, >=), resolves variable values
    from flat or nested design context dictionaries, evaluates the condition, and returns a structured `RuleEvaluationResult`.
"""

import time
import re
from typing import Any
from backend.rules.models.engineering_rule import EngineeringRule
from backend.rules.models.rule_evaluation_result import RuleEvaluationResult


class RuleEvaluatorError(ValueError):
    """Base exception class for RuleEvaluator errors."""
    pass


class InvalidRuleExpressionError(RuleEvaluatorError):
    """Raised when a rule condition expression is malformed or contains an unsupported operator."""
    pass


class MissingRuleContextError(RuleEvaluatorError, KeyError):
    """Raised when a context variable referenced in a rule expression cannot be resolved."""
    pass


class RuleEvaluator:
    """
    Evaluator for single EngineeringRule execution against design context.

    Supported Operators:
        `==`, `!=`, `<=`, `>=`, `<`, `>`

    Context Resolution Strategy:
        - Literal Parsing: Numbers (ints/floats), booleans (true/false), and quoted strings.
        - Direct Lookup: Matches exact keys in flat context dictionaries (e.g., 'motor.current').
        - Nested Path Lookup: Traverses nested context dictionaries (e.g., context['motor']['current']).

    Design Principles:
        - Single Responsibility Principle (SRP): Evaluates one rule only.
        - Open/Closed Principle (OCP): Extensible operator mapping and expression resolution.
        - Clean Architecture: Completely decoupled from graph traversals, ORMs, and databases.
    """

    OPERATORS: list[str] = ["<=", ">=", "==", "!=", "<", ">"]

    def evaluate(self, rule: EngineeringRule, context: dict[str, Any]) -> RuleEvaluationResult:
        """
        Evaluates a single EngineeringRule condition against a design context dictionary.

        Args:
            rule (EngineeringRule): The rule instance to evaluate.
            context (dict[str, Any]): Dictionary containing design state variables.

        Returns:
            RuleEvaluationResult: Structured diagnostic evaluation result.

        Raises:
            InvalidRuleExpressionError: If the condition expression is invalid or missing an operator.
            MissingRuleContextError: If a referenced context variable cannot be resolved.
        """
        start_time = time.perf_counter()

        condition_str = (rule.condition or "").strip()
        if not condition_str:
            raise InvalidRuleExpressionError(f"Rule '{rule.id}' has an empty or missing condition expression.")

        # Parse condition into LHS, Operator, and RHS
        lhs_str, op, rhs_str = self._parse_condition(condition_str, rule.id)

        # Resolve LHS and RHS values from context or literals
        lhs_val = self._resolve_value(lhs_str, context)
        rhs_val = self._resolve_value(rhs_str, context)

        # Perform comparison
        passed = self._compare(lhs_val, op, rhs_val)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        message = "" if passed else rule.message

        details: dict[str, Any] = {
            "lhs": lhs_str,
            "lhs_val": lhs_val,
            "operator": op,
            "rhs": rhs_str,
            "rhs_val": rhs_val,
        }

        return RuleEvaluationResult(
            rule_id=rule.id,
            passed=passed,
            severity=rule.severity,
            message=message,
            details=details,
            evaluation_time_ms=round(duration_ms, 3)
        )

    def _parse_condition(self, condition: str, rule_id: str) -> tuple[str, str, str]:
        """Parses a condition string into (lhs, operator, rhs)."""
        for op in self.OPERATORS:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    return parts[0].strip(), op, parts[1].strip()

        raise InvalidRuleExpressionError(
            f"Rule '{rule_id}' has an invalid expression: '{condition}'. "
            f"Condition must contain a valid comparison operator ({', '.join(self.OPERATORS)})."
        )

    def _resolve_value(self, expr: str, context: dict[str, Any]) -> Any:
        """Resolves an expression string into a concrete Python value from context or literal constants."""
        cleaned_expr = expr.strip()

        # 1. Try parsing numeric literal (int / float)
        try:
            if "." in cleaned_expr:
                return float(cleaned_expr)
            return int(cleaned_expr)
        except ValueError:
            pass

        # 2. Try parsing boolean literal
        if cleaned_expr.lower() == "true":
            return True
        if cleaned_expr.lower() == "false":
            return False

        # 3. Try parsing string literal (quoted)
        if (cleaned_expr.startswith('"') and cleaned_expr.endswith('"')) or (
            cleaned_expr.startswith("'") and cleaned_expr.endswith("'")
        ):
            return cleaned_expr[1:-1]

        # 4. Direct lookup in flat context
        if cleaned_expr in context:
            return context[cleaned_expr]

        # 5. Nested dictionary lookup (e.g. "motor.current" -> context["motor"]["current"])
        parts = cleaned_expr.split(".")
        curr: Any = context
        found = True

        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                found = False
                break

        if found:
            return curr

        raise MissingRuleContextError(
            f"Cannot resolve context variable '{cleaned_expr}' for rule evaluation."
        )

    def _compare(self, lhs: Any, op: str, rhs: Any) -> bool:
        """Compares LHS and RHS values using operator."""
        try:
            if op == "==":
                return lhs == rhs
            elif op == "!=":
                return lhs != rhs
            elif op == "<":
                return lhs < rhs
            elif op == "<=":
                return lhs <= rhs
            elif op == ">":
                return lhs > rhs
            elif op == ">=":
                return lhs >= rhs
        except TypeError as err:
            raise InvalidRuleExpressionError(
                f"Type error comparing '{lhs}' ({type(lhs).__name__}) {op} '{rhs}' ({type(rhs).__name__}): {err}"
            ) from err

        raise InvalidRuleExpressionError(f"Unsupported comparison operator: '{op}'.")
