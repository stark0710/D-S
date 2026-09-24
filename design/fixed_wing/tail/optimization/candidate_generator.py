"""
Fixed-Wing Tail Optimization Candidate Generator

Generates deterministic grid search candidates for empennage configuration
and sizing optimization.
"""

from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_generator_base import CandidateGeneratorBase


def _linspace(start: float, stop: float, steps: int) -> list[float]:
    """Generates evenly-spaced values between start and stop (inclusive)."""
    if steps <= 1:
        return [round(start, 4)]
    return [round(start + (stop - start) * i / (steps - 1), 4) for i in range(steps)]


class GridSearchCandidateGenerator(CandidateGeneratorBase):
    """
    Generates a uniform grid of tail configuration and sizing parameter candidates.

    Design variables per candidate:
        tail_configuration  — str (Conventional, T-Tail, V-Tail, Inverted V-Tail, Twin Boom)
        horizontal_V_h      — float (horizontal tail volume coefficient)
        vertical_V_v         — float (vertical tail volume coefficient)
        tail_arm_ratio       — float (tail arm as fraction of wingspan)
        horiz_ar             — float (horizontal tail aspect ratio)
        vert_ar              — float (vertical tail aspect ratio)
        horiz_taper          — float (horizontal tail taper ratio)
        vert_taper           — float (vertical tail taper ratio)
        horiz_sweep          — float (horizontal tail sweep angle, deg)
        vert_sweep           — float (vertical tail sweep angle, deg)
        tail_dihedral_deg    — float (tail dihedral angle, deg)
    """

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        configurations = ["Conventional", "T-Tail", "V-Tail", "Inverted V-Tail", "Twin Boom"]

        v_h_values = _linspace(0.45, 0.80, 3)
        v_v_values = _linspace(0.03, 0.06, 3)
        arm_ratios = _linspace(0.38, 0.62, 3)
        h_ar_values = _linspace(3.0, 6.0, 2)
        v_ar_values = _linspace(1.2, 2.5, 2)
        h_taper_values = _linspace(0.30, 1.0, 2)
        v_taper_values = _linspace(0.30, 1.0, 2)
        h_sweep_values = _linspace(0.0, 20.0, 2)
        v_sweep_values = _linspace(0.0, 20.0, 2)

        candidates = []
        for config in configurations:
            if config in ("V-Tail", "Inverted V-Tail"):
                dihedral_values = [35.0, 45.0] if config == "V-Tail" else [-45.0, -35.0]
            else:
                dihedral_values = [0.0]

            for dihedral in dihedral_values:
                for v_h in v_h_values:
                    for v_v in v_v_values:
                        for arm_ratio in arm_ratios:
                            for h_ar in h_ar_values:
                                for v_ar in v_ar_values:
                                    for h_taper in h_taper_values:
                                        for v_taper in v_taper_values:
                                            for h_sweep in h_sweep_values:
                                                for v_sweep in v_sweep_values:
                                                    candidates.append(
                                                        OptimizationCandidate(
                                                            design_variables={
                                                                "tail_configuration": config,
                                                                "horizontal_V_h": v_h,
                                                                "vertical_V_v": v_v,
                                                                "tail_arm_ratio": arm_ratio,
                                                                "horiz_ar": h_ar,
                                                                "vert_ar": v_ar,
                                                                "horiz_taper": h_taper,
                                                                "vert_taper": v_taper,
                                                                "horiz_sweep": h_sweep,
                                                                "vert_sweep": v_sweep,
                                                                "tail_dihedral_deg": dihedral,
                                                            }
                                                        )
                                                    )
        return candidates
