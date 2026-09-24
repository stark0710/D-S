"""
OptimizationResult Subsystem

Purpose:
    Defines the `OptimizationResult` domain model representing output from the Drone Design Optimization Engineering Framework.

Role in Architecture:
    `OptimizationResult` encapsulates `best_design` (tuple of PerformanceResult & MassResult), `candidate_designs`, `pareto_front`,
    `tradeoff_analysis` (TradeoffAnalysisResult), `objective_scores` (ObjectiveScores), `optimization_iterations` (int),
    improvement summary, engineering notes, warnings, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.drone.optimization.objective_function import ObjectiveScores
from backend.design.drone.optimization.tradeoff_analysis import TradeoffAnalysisResult
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.mass_properties.mass_result import MassResult


@dataclass(slots=True)
class OptimizationResult:
    """
    Multirotor design optimization engineering output summary.

    Attributes:
        best_design (tuple[PerformanceResult, MassResult]): Best optimized performance and mass result pair.
        candidate_designs (list[tuple[PerformanceResult, MassResult]]): List of generated candidate design pairs.
        pareto_front (list[tuple[PerformanceResult, MassResult]]): Non-dominated Pareto optimal candidate set.
        tradeoff_analysis (TradeoffAnalysisResult): Baseline vs optimized design trade-off analysis.
        objective_scores (ObjectiveScores): Objective score summary for the best design.
        optimization_iterations (int): Total optimization search iterations executed.
        improvement_summary (str): Summary description of achieved engineering improvements.
        engineering_notes (str): Rationale and engineering notes.
        warnings (list[str]): Diagnostic warnings generated during optimization.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    best_design: tuple[PerformanceResult, MassResult]
    candidate_designs: list[tuple[PerformanceResult, MassResult]]
    pareto_front: list[tuple[PerformanceResult, MassResult]]
    tradeoff_analysis: TradeoffAnalysisResult
    objective_scores: ObjectiveScores
    optimization_iterations: int
    improvement_summary: str
    engineering_notes: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
