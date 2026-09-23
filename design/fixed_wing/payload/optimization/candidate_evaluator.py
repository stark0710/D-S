"""
Fixed-Wing Payload Sizing Candidate Evaluator

Evaluates layout geometry details and populates coordinate properties.
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_evaluator_base import CandidateEvaluatorBase
from backend.design.fixed_wing.payload.optimization.constraints import map_layout_coordinates

class CandidateEvaluator(CandidateEvaluatorBase):
    """
    Evaluator mapping discrete candidate variables to physical coordinates and calculating metrics.
    """
    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        coords = map_layout_coordinates(candidate, context)
        
        candidate.derived_variables["payload_position"] = coords["payload_x"]
        candidate.derived_variables["battery_position"] = coords["battery_x"]
        candidate.derived_variables["gps_position"] = coords["gps_x"]
        candidate.derived_variables["receiver_position"] = coords["receiver_x"]
        candidate.derived_variables["telemetry_position"] = coords["telemetry_x"]
        
        # Packaging efficiency metric based on layout mode
        e_mode = candidate.design_variables["electronics_layout_mode"]
        if e_mode in ["Stacked Above", "Stacked Below"]:
            efficiency = 0.88  # Higher density efficiency when stacked
        elif e_mode == "Side Mounted":
            efficiency = 0.82
        else:
            efficiency = 0.75
            
        candidate.derived_variables["packing_efficiency"] = efficiency
