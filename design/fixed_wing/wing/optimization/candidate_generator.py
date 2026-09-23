"""
Fixed-Wing Wing Planform Sizing Candidate Generator

Generates deterministic grid sweeps over Aspect Ratio, Taper, Sweep, and Dihedral variables.
"""

from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_generator_base import CandidateGeneratorBase

class GridSearchCandidateGenerator(CandidateGeneratorBase):
    """
    Generates a uniform, multi-dimensional parameter search space of candidates.
    """
    def __init__(
        self,
        ar_range: tuple[float, float, float] = (8.0, 16.0, 1.0),
        taper_range: tuple[float, float, float] = (0.35, 1.00, 0.05),
        sweep_range: tuple[float, float, float] = (0.0, 10.0, 2.0),
        dihedral_range: tuple[float, float, float] = (0.0, 6.0, 1.0)
    ) -> None:
        self.ar_range = ar_range
        self.taper_range = taper_range
        self.sweep_range = sweep_range
        self.dihedral_range = dihedral_range

    def _arange(self, start: float, end: float, step: float) -> List[float]:
        vals = []
        curr = start
        while curr <= end + 1e-9:
            vals.append(round(curr, 4))
            curr += step
        return vals

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        ar_vals = self._arange(*self.ar_range)
        taper_vals = self._arange(*self.taper_range)
        sweep_vals = self._arange(*self.sweep_range)
        dihedral_vals = self._arange(*self.dihedral_range)

        planform_style = "Tapered"
        wing_position = "High Wing"
        if context.configuration:
            # Handle both dictionary and class configurations
            if hasattr(context.configuration, "selected_configuration"):
                layout = context.configuration.selected_configuration
            elif isinstance(context.configuration, dict):
                layout = context.configuration
            else:
                layout = {}
            wing_position = layout.get("wing_position", "High Wing")
            planform_style = layout.get("wing_planform_style", "Tapered")

        candidates = []
        for ar in ar_vals:
            for taper in taper_vals:
                for sweep in sweep_vals:
                    for dihedral in dihedral_vals:
                        candidates.append(
                            OptimizationCandidate(
                                design_variables={
                                    "aspect_ratio": ar,
                                    "taper_ratio": taper,
                                    "sweep_angle_deg": sweep,
                                    "dihedral_angle_deg": dihedral,
                                    "wing_position": wing_position,
                                    "planform_style": planform_style
                                }
                            )
                        )
        return candidates
