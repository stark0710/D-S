"""
ScoringPipeline Subsystem

Purpose:
    Defines the `ScoringPipeline` class responsible for executing quantitative scoring rules and applying priority weighting.

Role in Architecture:
    `ScoringPipeline` coordinates rule evaluations, applies priority-based weighting (Balanced, Payload, Endurance, Cost, Efficiency),
    aggregates category score breakdowns, calculates overall normalized engineering scores, and identifies design strengths/weaknesses.
"""

from typing import Any
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.components.scoring.score_category import ScoreCategory
from backend.design.components.scoring.score_breakdown import ScoreBreakdown
from backend.design.components.scoring.engineering_score import EngineeringScore
from backend.design.components.scoring.scoring_rule import ScoringRule


def _resolve_weights(priority: OptimizationPriority | None) -> dict[ScoreCategory, float]:
    """Helper returning category weight dictionary for given OptimizationPriority."""
    if priority == OptimizationPriority.MAXIMUM_PAYLOAD:
        return {
            ScoreCategory.PAYLOAD: 0.35,
            ScoreCategory.ENDURANCE: 0.15,
            ScoreCategory.COST: 0.15,
            ScoreCategory.WEIGHT: 0.15,
            ScoreCategory.SAFETY: 0.10,
            ScoreCategory.RANGE: 0.10,
        }
    elif priority == OptimizationPriority.MAXIMUM_ENDURANCE:
        return {
            ScoreCategory.ENDURANCE: 0.35,
            ScoreCategory.RANGE: 0.20,
            ScoreCategory.PAYLOAD: 0.15,
            ScoreCategory.COST: 0.10,
            ScoreCategory.WEIGHT: 0.10,
            ScoreCategory.SAFETY: 0.10,
        }
    elif priority == OptimizationPriority.LOWEST_COST:
        return {
            ScoreCategory.COST: 0.45,
            ScoreCategory.WEIGHT: 0.15,
            ScoreCategory.PAYLOAD: 0.10,
            ScoreCategory.ENDURANCE: 0.10,
            ScoreCategory.RANGE: 0.10,
            ScoreCategory.SAFETY: 0.10,
        }
    elif priority in (OptimizationPriority.HIGHEST_EFFICIENCY, OptimizationPriority.MAXIMUM_RANGE):
        return {
            ScoreCategory.EFFICIENCY: 0.30,
            ScoreCategory.ENDURANCE: 0.20,
            ScoreCategory.RANGE: 0.20,
            ScoreCategory.COST: 0.10,
            ScoreCategory.WEIGHT: 0.10,
            ScoreCategory.SAFETY: 0.10,
        }
    else:  # BALANCED default
        return {
            ScoreCategory.PAYLOAD: 0.18,
            ScoreCategory.ENDURANCE: 0.18,
            ScoreCategory.RANGE: 0.16,
            ScoreCategory.COST: 0.16,
            ScoreCategory.WEIGHT: 0.16,
            ScoreCategory.SAFETY: 0.16,
        }


class ScoringPipeline:
    """
    Pipeline for executing quantitative category scoring rules.

    Design Principles:
        - Pipeline Pattern: Sequential execution of category scoring rules.
        - Strategy & Weighting: Supports configurable weights based on OptimizationPriority without altering rule logic.
    """

    def __init__(self, rules: list[ScoringRule] | None = None) -> None:
        """
        Initializes the ScoringPipeline.

        Args:
            rules (list[ScoringRule] | None): Optional initial list of scoring rules.
        """
        self._rules: list[ScoringRule] = list(rules) if rules else []

    def register_rule(self, rule: ScoringRule) -> None:
        """Registers a new scoring rule into the pipeline."""
        self._rules.append(rule)

    def execute(
        self,
        design_data: dict[str, Any],
        context: Any | None = None,
        custom_weights: dict[ScoreCategory, float] | None = None
    ) -> EngineeringScore:
        """
        Executes quantitative scoring against design data and context.

        Args:
            design_data (dict[str, Any]): Aircraft design data dictionary.
            context (Any | None): Optional DesignContext instance.
            custom_weights (dict[ScoreCategory, float] | None): Optional custom weighting override dictionary.

        Returns:
            EngineeringScore: Aggregated quantitative engineering score result.
        """
        priority = None
        if context and getattr(context, "requirement_model", None):
            priority = context.requirement_model.optimization_priority

        weights = custom_weights if custom_weights else _resolve_weights(priority)

        breakdowns: list[ScoreBreakdown] = []
        total_weighted = 0.0
        total_max = 0.0
        strengths: list[str] = []
        weaknesses: list[str] = []
        recs: list[str] = []

        for rule in self._rules:
            raw, comment = rule.evaluate(design_data, context)
            w = weights.get(rule.category, 0.15)
            weighted = raw * w
            max_possible = w

            total_weighted += weighted
            total_max += max_possible

            breakdown = ScoreBreakdown(
                category=rule.category,
                raw_score=round(raw, 2),
                weighted_score=round(weighted, 3),
                maximum_score=round(max_possible, 3),
                comments=comment
            )
            breakdowns.append(breakdown)

            if raw >= 0.85:
                strengths.append(f"High performance in {rule.category.value}: {comment}")
            elif raw < 0.60:
                weaknesses.append(f"Sub-optimal performance in {rule.category.value}: {comment}")
                recs.append(f"Improve {rule.category.value} to optimize overall design score.")

        overall = total_weighted / total_max if total_max > 0 else 0.0
        overall = max(0.0, min(1.0, overall))

        return EngineeringScore(
            overall_score=round(overall, 3),
            score_breakdown=breakdowns,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recs,
            metadata={"rule_count": len(self._rules), "priority": priority.value if priority else "BALANCED"}
        )
