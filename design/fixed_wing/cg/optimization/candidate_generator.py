"""
Fixed-Wing Center of Gravity (CG) Optimization Candidate Generator
"""

from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class CGCandidateGenerator:
    """
    Generates placement sweeps for movable aircraft components (battery, payload, avionics)
    within the fuselage cabin volume to balance Center of Gravity.
    """
    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        # Finer grid search to maximize chance of satisfying tight clearance constraints
        battery_fractions = [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85]
        payload_fractions = [0.18, 0.28, 0.38, 0.48, 0.58, 0.68, 0.78, 0.88]
        avionics_fractions = [0.10, 0.25, 0.40, 0.55, 0.70, 0.85]

        candidates = []
        for bf in battery_fractions:
            for pf in payload_fractions:
                for af in avionics_fractions:
                    dv = {
                        "battery_pos_fraction": bf,
                        "payload_pos_fraction": pf,
                        "avionics_pos_fraction": af,
                    }
                    candidates.append(OptimizationCandidate(
                        design_variables=dv,
                        derived_variables={},
                        objective_scores={},
                        status="PENDING",
                    ))
        return candidates
