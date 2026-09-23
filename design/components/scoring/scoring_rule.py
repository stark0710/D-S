"""
ScoringRule Subsystem

Purpose:
    Defines the abstract `ScoringRule` interface and concrete category scoring rules.

Role in Architecture:
    `ScoringRule` evaluates a specific quantitative performance category (Payload, Endurance, Range, Cost, Efficiency, Weight, Safety)
    against design data and returns an unweighted raw score (0.0 to 1.0) with comments.
"""

from abc import ABC, abstractmethod
from typing import Any
from backend.design.components.scoring.score_category import ScoreCategory


class ScoringRule(ABC):
    """
    Abstract interface for quantitative category scoring rules.
    """

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Unique identifier name of the rule implementation."""
        pass

    @property
    @abstractmethod
    def category(self) -> ScoreCategory:
        """Target ScoreCategory evaluated by this rule."""
        pass

    @abstractmethod
    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> tuple[float, str]:
        """
        Evaluates category raw score and comments.

        Args:
            design_data (dict[str, Any]): Aircraft design data dictionary.
            context (Any | None): Optional DesignContext instance.

        Returns:
            tuple[float, str]: Tuple of (raw_score from 0.0 to 1.0, explanatory comment).
        """
        pass


class PayloadScoreRule(ScoringRule):
    """Evaluates payload mass capacity match score."""

    @property
    def rule_name(self) -> str:
        return "PayloadScoreRule"

    @property
    def category(self) -> ScoreCategory:
        return ScoreCategory.PAYLOAD

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> tuple[float, str]:
        actual = float(design_data.get("payload_capacity_kg", 0))

        required = 0.0
        if context and getattr(context, "requirement_model", None):
            required = float(context.requirement_model.payload_weight_kg)
        elif "required_payload_kg" in design_data:
            required = float(design_data["required_payload_kg"])

        if required <= 0:
            return 1.0, "No payload requirement specified; maximum score assigned."

        ratio = actual / required
        score = min(1.0, max(0.0, ratio))
        comment = f"Payload capacity match: {actual:.2f} kg / {required:.2f} kg requirement (Ratio: {ratio:.2f})."
        return score, comment


class EnduranceScoreRule(ScoringRule):
    """Evaluates flight endurance time match score."""

    @property
    def rule_name(self) -> str:
        return "EnduranceScoreRule"

    @property
    def category(self) -> ScoreCategory:
        return ScoreCategory.ENDURANCE

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> tuple[float, str]:
        actual = float(design_data.get("endurance_min", 0))

        required = 0.0
        if context and getattr(context, "requirement_model", None):
            required = float(context.requirement_model.target_flight_time_min)
        elif "required_flight_time_min" in design_data:
            required = float(design_data["required_flight_time_min"])

        if required <= 0:
            return 1.0, "No flight time requirement specified; maximum score assigned."

        ratio = actual / required
        score = min(1.0, max(0.0, ratio))
        comment = f"Endurance flight time match: {actual:.1f} min / {required:.1f} min requirement (Ratio: {ratio:.2f})."
        return score, comment


class RangeScoreRule(ScoringRule):
    """Evaluates operational range match score."""

    @property
    def rule_name(self) -> str:
        return "RangeScoreRule"

    @property
    def category(self) -> ScoreCategory:
        return ScoreCategory.RANGE

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> tuple[float, str]:
        actual = float(design_data.get("range_km", 0))

        required = 0.0
        if context and getattr(context, "requirement_model", None):
            required = float(context.requirement_model.target_range_km)
        elif "required_range_km" in design_data:
            required = float(design_data["required_range_km"])

        if required <= 0:
            return 1.0, "No range requirement specified; maximum score assigned."

        ratio = actual / required
        score = min(1.0, max(0.0, ratio))
        comment = f"Range distance match: {actual:.1f} km / {required:.1f} km requirement (Ratio: {ratio:.2f})."
        return score, comment


class CostScoreRule(ScoringRule):
    """Evaluates cost efficiency relative to budget limit."""

    @property
    def rule_name(self) -> str:
        return "CostScoreRule"

    @property
    def category(self) -> ScoreCategory:
        return ScoreCategory.COST

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> tuple[float, str]:
        actual_cost = float(design_data.get("estimated_cost", 0))

        budget = None
        if context and getattr(context, "requirement_model", None):
            budget = context.requirement_model.budget
        elif "budget_limit" in design_data:
            budget = float(design_data["budget_limit"])

        if not budget or budget <= 0:
            return 0.80, f"No budget specified; default cost score evaluated for estimated cost ${actual_cost:.2f}."

        if actual_cost <= 0:
            return 1.0, "Zero estimated cost."

        if actual_cost > budget:
            return 0.0, f"Cost (${actual_cost:.2f}) exceeds budget (${budget:.2f})."

        savings_ratio = (budget - actual_cost) / budget
        score = 0.50 + (savings_ratio * 0.50)
        score = min(1.0, max(0.0, score))
        comment = f"Cost score: ${actual_cost:.2f} against ${budget:.2f} budget ({savings_ratio*100:.1f}% under budget)."
        return score, comment


class WeightScoreRule(ScoringRule):
    """Evaluates structural weight margin score."""

    @property
    def rule_name(self) -> str:
        return "WeightScoreRule"

    @property
    def category(self) -> ScoreCategory:
        return ScoreCategory.WEIGHT

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> tuple[float, str]:
        actual_mtow = float(design_data.get("mtow_kg", 0))

        mtow_limit = None
        if context and getattr(context, "requirement_model", None):
            mtow_limit = context.requirement_model.maximum_takeoff_weight_kg
        elif "limit_mtow_kg" in design_data:
            mtow_limit = float(design_data["limit_mtow_kg"])

        if not mtow_limit or mtow_limit <= 0:
            return 0.85, f"No MTOW limit specified; weight score evaluated for MTOW {actual_mtow:.2f} kg."

        if actual_mtow > mtow_limit:
            return 0.0, f"MTOW ({actual_mtow:.2f} kg) exceeds limit ({mtow_limit:.2f} kg)."

        margin = (mtow_limit - actual_mtow) / mtow_limit
        score = 0.60 + (margin * 0.40)
        score = min(1.0, max(0.0, score))
        comment = f"Weight score: MTOW {actual_mtow:.2f} kg has {margin*100:.1f}% margin below {mtow_limit:.2f} kg limit."
        return score, comment


class SafetyScoreRule(ScoringRule):
    """Evaluates thrust-to-weight and control safety score."""

    @property
    def rule_name(self) -> str:
        return "SafetyScoreRule"

    @property
    def category(self) -> ScoreCategory:
        return ScoreCategory.SAFETY

    def evaluate(self, design_data: dict[str, Any], context: Any | None = None) -> tuple[float, str]:
        t_w = float(design_data.get("thrust_to_weight_ratio", 2.0))

        if t_w >= 2.2:
            score = 1.0
            comment = f"Excellent safety margin (T/W ratio = {t_w:.2f})."
        elif t_w >= 1.8:
            score = 0.85
            comment = f"Good safety margin (T/W ratio = {t_w:.2f})."
        elif t_w >= 1.5:
            score = 0.60
            comment = f"Adequate safety margin (T/W ratio = {t_w:.2f})."
        else:
            score = 0.20
            comment = f"Low safety margin (T/W ratio = {t_w:.2f})."

        return score, comment
