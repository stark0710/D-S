"""
Fixed-Wing Payload Packaging Candidate Generator

Generates discrete layout configurations representing various internal equipment arrangements.
"""

from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_generator_base import CandidateGeneratorBase

class GridSearchCandidateGenerator(CandidateGeneratorBase):
    """
    Generates a uniform sweep of discrete equipment packaging strategies.
    """
    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        payload_positions = ["Forward", "Mid", "Rear"]
        battery_positions = ["Forward", "Mid", "Rear"]
        battery_orientations = ["Longitudinal", "Lateral"]
        electronics_layouts = ["Stacked Above", "Stacked Below", "Side Mounted"]
        
        candidates = []
        for p_pos in payload_positions:
            for b_pos in battery_positions:
                # Basic sanity: payload and battery position modes shouldn't match to avoid simple conflicts
                if p_pos == b_pos:
                    continue
                for b_ori in battery_orientations:
                    for e_lay in electronics_layouts:
                        candidates.append(
                            OptimizationCandidate(
                                design_variables={
                                    "payload_position_mode": p_pos,
                                    "battery_position_mode": b_pos,
                                    "battery_orientation": b_ori,
                                    "electronics_layout_mode": e_lay
                                }
                            )
                        )
        return candidates
