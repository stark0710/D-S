"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Framework

Exposes common classes for optimization contexts, candidates, builders, constraints, and objective scores.
"""

from backend.design.common.optimization.optimization_context import (
    OptimizationContext,
)
from backend.design.common.optimization.optimization_candidate import (
    OptimizationCandidate,
)
from backend.design.common.optimization.optimization_result import (
    OptimizationResult,
)
from backend.design.common.optimization.candidate_generator_base import (
    CandidateGeneratorBase,
)
from backend.design.common.optimization.candidate_evaluator_base import (
    CandidateEvaluatorBase,
)
from backend.design.common.optimization.constraint_manager import (
    Constraint,
    ConstraintManager,
)
from backend.design.common.optimization.objective_function import (
    ObjectiveTerm,
    ObjectiveFunction,
)
from backend.design.common.optimization.optimization_logger import (
    OptimizationLogger,
)
from backend.design.common.optimization.optimization_report import (
    OptimizationReport,
)
from backend.design.common.optimization.optimization_utils import (
    TimingHelper,
    normalize_value,
    weighted_sum,
    format_diagnostics,
)
from backend.design.common.optimization.optimizer_base import (
    OptimizerBase,
)
