"""
Fixed-Wing Tail Optimization Subsystem

Exposes the tail optimizer, specification, constraints, and scoring components
using the Shared Optimization Framework.
"""

from backend.design.fixed_wing.tail.optimization.models import (
    TailSpecification,
)
from backend.design.fixed_wing.tail.optimization.result import (
    TailOptimizationResult,
)
from backend.design.fixed_wing.tail.optimization.candidate_generator import (
    GridSearchCandidateGenerator,
)
from backend.design.fixed_wing.tail.optimization.candidate_evaluator import (
    CandidateEvaluator,
)
from backend.design.fixed_wing.tail.optimization.constraints import (
    build_tail_constraints,
)
from backend.design.fixed_wing.tail.optimization.objective_function import (
    TailObjectiveFunction,
)
from backend.design.fixed_wing.tail.optimization.tail_optimizer import (
    TailOptimizer,
)
