"""
Fixed-Wing Fuselage Sizing Candidate Generator

Generates deterministic grid sweeps over Length, Width, Height, Fineness, and Cross Section shape variables.
"""

from typing import List
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_generator_base import CandidateGeneratorBase

class GridSearchCandidateGenerator(CandidateGeneratorBase):
    """
    Generates a uniform, multi-dimensional parameter search space of fuselage candidates.
    """
    def __init__(
        self,
        length_range: tuple[float, float, float] = (0.6, 3.5, 0.7),
        width_range: tuple[float, float, float] = (0.10, 0.45, 0.05),
        height_range: tuple[float, float, float] = (0.10, 0.45, 0.10),
        fineness_range: tuple[float, float, float] = (5.0, 12.0, 3.0),
        cross_sections: List[str] = None
    ) -> None:
        self.length_range = length_range
        self.width_range = width_range
        self.height_range = height_range
        self.fineness_range = fineness_range
        self.cross_sections = cross_sections if cross_sections else ["Circular", "Rectangular"]

    def _arange(self, start: float, end: float, step: float) -> List[float]:
        vals = []
        curr = start
        while curr <= end + 1e-9:
            vals.append(round(curr, 4))
            curr += step
        return vals

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        lengths = self._arange(*self.length_range)
        widths = self._arange(*self.width_range)
        heights = self._arange(*self.height_range)
        fineness_ratios = self._arange(*self.fineness_range)

        # Ensure baseline sized fuselage dimensions are evaluated
        reqs = getattr(context, "requirements", None)
        if reqs:
            fuse_res = getattr(reqs, "fuselage_result", None)
            if fuse_res and hasattr(fuse_res, "fuselage_geometry"):
                base_w = round(fuse_res.fuselage_geometry.width_m, 3)
                if base_w not in widths and self.width_range[0] <= base_w <= self.width_range[1]:
                    widths.append(base_w)
            widths.sort()

        candidates = []
        for l in lengths:
            for w in widths:
                for h in heights:
                    for fr in fineness_ratios:
                        for cs in self.cross_sections:
                            nose_l = round(l * 0.18, 3)
                            tail_cone_l = round(l * 0.40, 3)
                            cabin_l = round(l - nose_l - tail_cone_l, 3)
                            
                            bulkheads = [0.0, nose_l, nose_l + cabin_l, l]

                            candidates.append(
                                OptimizationCandidate(
                                    design_variables={
                                        "length": l,
                                        "width": w,
                                        "height": h,
                                        "fineness_ratio": fr,
                                        "cross_section": cs,
                                        "nose_length": nose_l,
                                        "cabin_length": cabin_l,
                                        "tail_cone_length": tail_cone_l,
                                        "bulkhead_locations": bulkheads
                                    }
                                )
                            )
        return candidates
