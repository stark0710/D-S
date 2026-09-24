"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Candidate Generator Base

Abstract base class for sweeps generators.
"""

from abc import ABC, abstractmethod
from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate

class CandidateGeneratorBase(ABC):
    """
    Abstract generator class. Subclasses must implement generate_candidates.
    """
    @abstractmethod
    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Generates design parameter candidates to evaluate.
        """
        pass
