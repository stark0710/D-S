"""
Fixed-Wing Flight Performance Candidate Generator
"""

from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class FlightPerformanceCandidateGenerator:
    """
    Generates a single candidate representing the baseline aircraft design configuration
    for comprehensive flight performance analysis.
    """
    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        # Only evaluate the single baseline candidate
        return [
            OptimizationCandidate(
                design_variables={},
                derived_variables={},
                objective_scores={},
                status="PENDING",
            )
        ]
