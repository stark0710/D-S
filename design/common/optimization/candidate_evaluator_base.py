"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Candidate Evaluator Base

Abstract base class for running physics/engineering calculation backends.
"""

from abc import ABC, abstractmethod
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

class CandidateEvaluatorBase(ABC):
    """
    Abstract evaluator class. Subclasses must implement evaluate.
    """
    @abstractmethod
    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Executes sizing tools/engines to populate candidate properties.
        """
        pass
