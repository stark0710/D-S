"""
ConstraintRule Subsystem

Purpose:
    Defines the abstract `ConstraintRule` interface and concrete engineering constraint validation rules.

Role in Architecture:
    `ConstraintRule` encapsulates a single aircraft engineering constraint evaluation check (Payload, MTOW, Budget, Endurance, Range, T/W).
"""

from abc import ABC, abstractmethod
from typing import Any
from backend.design.components.constraints.constraint_severity import ConstraintSeverity
from backend.design.components.constraints.constraint_issue import ConstraintIssue


class ConstraintRule(ABC):
    """
    Abstract interface for aircraft engineering constraint rules.
    """

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Unique identifier name of the rule implementation."""
        pass

    @property
    @abstractmethod
    def constraint_name(self) -> str:
        """Name of the engineering constraint evaluated by this rule."""
        pass

    @abstractmethod
    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> list[ConstraintIssue]:
        """
        Evaluates the constraint against design data and optional context.

        Args:
            design_data (dict[str, Any]): Aircraft design data dictionary.
            context (Any | None): Optional DesignContext instance.

        Returns:
            list[ConstraintIssue]: Identified constraint issues.
        """
        pass


class PayloadConstraintRule(ConstraintRule):
    """Evaluates whether aircraft payload capacity satisfies mission payload requirement."""

    @property
    def rule_name(self) -> str:
        return "PayloadConstraintRule"

    @property
    def constraint_name(self) -> str:
        return "PayloadCapacity"

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> list[ConstraintIssue]:
        issues: list[ConstraintIssue] = []
        actual = float(design_data.get("payload_capacity_kg", 0))

        required = 0.0
        if context and getattr(context, "requirement_model", None):
            required = float(context.requirement_model.payload_weight_kg)
        elif "required_payload_kg" in design_data:
            required = float(design_data["required_payload_kg"])

        if required > 0:
            if actual < required:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.CRITICAL,
                        constraint_name=self.constraint_name,
                        expected_value=required,
                        actual_value=actual,
                        message=f"Payload capacity ({actual} kg) is less than required payload mass ({required} kg).",
                        recommendation="Increase airframe structural volume or select higher thrust propulsion components."
                    )
                )

        return issues


class MaximumTakeoffWeightConstraintRule(ConstraintRule):
    """Evaluates whether total MTOW remains within upper MTOW limit."""

    @property
    def rule_name(self) -> str:
        return "MaximumTakeoffWeightConstraintRule"

    @property
    def constraint_name(self) -> str:
        return "MaximumTakeoffWeight"

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> list[ConstraintIssue]:
        issues: list[ConstraintIssue] = []
        actual_mtow = float(design_data.get("mtow_kg", 0))

        limit_mtow = None
        if context and getattr(context, "requirement_model", None):
            limit_mtow = context.requirement_model.maximum_takeoff_weight_kg
        elif "limit_mtow_kg" in design_data:
            limit_mtow = float(design_data["limit_mtow_kg"])

        if limit_mtow is not None and limit_mtow > 0 and actual_mtow > 0:
            if actual_mtow > limit_mtow:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.CRITICAL,
                        constraint_name=self.constraint_name,
                        expected_value=limit_mtow,
                        actual_value=actual_mtow,
                        message=f"Calculated MTOW ({actual_mtow} kg) exceeds maximum MTOW limit ({limit_mtow} kg).",
                        recommendation="Optimize component weights or switch to lighter structural materials."
                    )
                )

        return issues


class BudgetConstraintRule(ConstraintRule):
    """Evaluates estimated system component cost against financial budget limit."""

    @property
    def rule_name(self) -> str:
        return "BudgetConstraintRule"

    @property
    def constraint_name(self) -> str:
        return "FinancialBudget"

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> list[ConstraintIssue]:
        issues: list[ConstraintIssue] = []
        estimated_cost = float(design_data.get("estimated_cost", 0))

        budget = None
        if context and getattr(context, "requirement_model", None):
            budget = context.requirement_model.budget
        elif "budget_limit" in design_data:
            budget = float(design_data["budget_limit"])

        if budget is not None and budget > 0 and estimated_cost > 0:
            if estimated_cost > budget:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.CRITICAL,
                        constraint_name=self.constraint_name,
                        expected_value=budget,
                        actual_value=estimated_cost,
                        message=f"Estimated system cost (${estimated_cost}) exceeds budget limit (${budget}).",
                        recommendation="Select lower cost commercial off-the-shelf (COTS) components."
                    )
                )
            elif estimated_cost > 0.90 * budget:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.WARNING,
                        constraint_name=self.constraint_name,
                        expected_value=budget,
                        actual_value=estimated_cost,
                        message=f"Estimated system cost (${estimated_cost}) operates near upper budget limit (${budget}).",
                        recommendation="Monitor component pricing buffer."
                    )
                )

        return issues


class FlightTimeConstraintRule(ConstraintRule):
    """Evaluates calculated endurance flight time against target endurance requirement."""

    @property
    def rule_name(self) -> str:
        return "FlightTimeConstraintRule"

    @property
    def constraint_name(self) -> str:
        return "FlightTimeEndurance"

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> list[ConstraintIssue]:
        issues: list[ConstraintIssue] = []
        actual = float(design_data.get("endurance_min", 0))

        required = 0.0
        if context and getattr(context, "requirement_model", None):
            required = float(context.requirement_model.target_flight_time_min)
        elif "required_flight_time_min" in design_data:
            required = float(design_data["required_flight_time_min"])

        if required > 0 and actual > 0:
            if actual < required:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.CRITICAL,
                        constraint_name=self.constraint_name,
                        expected_value=required,
                        actual_value=actual,
                        message=f"Calculated endurance ({actual} min) falls short of required flight time ({required} min).",
                        recommendation="Increase battery pack capacity or improve aerodynamic cruise efficiency."
                    )
                )

        return issues


class RangeConstraintRule(ConstraintRule):
    """Evaluates calculated operational range against target range requirement."""

    @property
    def rule_name(self) -> str:
        return "RangeConstraintRule"

    @property
    def constraint_name(self) -> str:
        return "OperationalRange"

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> list[ConstraintIssue]:
        issues: list[ConstraintIssue] = []
        actual = float(design_data.get("range_km", 0))

        required = 0.0
        if context and getattr(context, "requirement_model", None):
            required = float(context.requirement_model.target_range_km)
        elif "required_range_km" in design_data:
            required = float(design_data["required_range_km"])

        if required > 0 and actual > 0:
            if actual < required:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.CRITICAL,
                        constraint_name=self.constraint_name,
                        expected_value=required,
                        actual_value=actual,
                        message=f"Calculated range ({actual} km) falls short of target range requirement ({required} km).",
                        recommendation="Increase battery energy capacity or select higher efficiency propulsion."
                    )
                )

        return issues


class ThrustToWeightConstraintRule(ConstraintRule):
    """Evaluates thrust-to-weight ratio safety margins."""

    @property
    def rule_name(self) -> str:
        return "ThrustToWeightConstraintRule"

    @property
    def constraint_name(self) -> str:
        return "ThrustToWeightRatio"

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> list[ConstraintIssue]:
        issues: list[ConstraintIssue] = []
        t_w = float(design_data.get("thrust_to_weight_ratio", 0))

        if t_w > 0:
            if t_w < 1.5:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.CRITICAL,
                        constraint_name=self.constraint_name,
                        expected_value=1.8,
                        actual_value=t_w,
                        message=f"Thrust-to-weight ratio ({t_w}) is dangerously low for safe flight control.",
                        recommendation="Increase motor thrust or reduce total vehicle mass."
                    )
                )
            elif t_w < 1.8:
                issues.append(
                    ConstraintIssue(
                        rule_name=self.rule_name,
                        severity=ConstraintSeverity.WARNING,
                        constraint_name=self.constraint_name,
                        expected_value=1.8,
                        actual_value=t_w,
                        message=f"Thrust-to-weight ratio ({t_w}) is low; control response in high winds will be degraded.",
                        recommendation="Consider increasing motor thrust for control authority."
                    )
                )

        return issues
