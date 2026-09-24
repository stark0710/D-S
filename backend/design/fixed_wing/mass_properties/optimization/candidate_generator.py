"""
Fixed-Wing Mass Properties Optimization Candidate Generator
"""

from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class MassCandidateGenerator:
    """
    Generates alternative weight build-up candidates by varying manufacturing,
    finishing, fasteners, and safety growth margins.
    """
    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        # Define parametric combinations to explore
        structural_margins = [1.0, 1.05, 1.10]
        fastener_allowances = [0.03, 0.05]  # percentage of empty structure
        paint_finish_types = ["None", "Standard Paint"]  # None=0g/m2, Standard=25g/m2
        safety_growth_margins = [0.05, 0.10]  # percentage added to MTOW

        candidates = []
        for sm in structural_margins:
            for fa in fastener_allowances:
                for pft in paint_finish_types:
                    for sg in safety_growth_margins:
                        dv = {
                            "structural_margin": sm,
                            "fastener_allowance": fa,
                            "paint_finish_type": pft,
                            "safety_growth_margin": sg,
                        }
                        candidates.append(OptimizationCandidate(
                            design_variables=dv,
                            derived_variables={},
                            objective_scores={},
                            status="PENDING",
                        ))
        return candidates
