"""
Torq Wings Fixed-Wing Pareto Front Extraction Subsystem (Phase 6B-6).
"""

from backend.design.fixed_wing.optimization.pareto.models import (
    ObjectiveDirection,
    ParetoObjectiveDefinition,
    ParetoObjectiveValue,
    ParetoTolerance,
    ParetoCandidate,
    ParetoFrontResult,
)
from backend.design.fixed_wing.optimization.pareto.dominance import (
    check_dominance,
    is_duplicate,
)
from backend.design.fixed_wing.optimization.pareto.extractor import (
    DEFAULT_OBJECTIVE_DEFINITIONS,
    ParetoFrontExtractor,
    build_candidate_from_result,
    self_check_pareto_front,
)

__all__ = [
    "ObjectiveDirection",
    "ParetoObjectiveDefinition",
    "ParetoObjectiveValue",
    "ParetoTolerance",
    "ParetoCandidate",
    "ParetoFrontResult",
    "check_dominance",
    "is_duplicate",
    "DEFAULT_OBJECTIVE_DEFINITIONS",
    "ParetoFrontExtractor",
    "build_candidate_from_result",
    "self_check_pareto_front",
]
