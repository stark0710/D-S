"""
Fixed-Wing Wing Planform Candidate Generator

Generates wing planform candidates using deterministic grid search or randomized searches.
"""

import random
from typing import List
from backend.design.fixed_wing.optimization.optimization_models import PlanformCandidate, OptimizationBounds

class CandidateGenerator:
    """
    Base class for planform candidate generation.
    """
    def generate(self, bounds: OptimizationBounds) -> List[PlanformCandidate]:
        raise NotImplementedError("Subclasses must implement generate().")

def linspace(start: float, end: float, steps: int) -> List[float]:
    """Generates evenly spaced values over a specified interval."""
    if steps <= 1:
        return [start]
    return [start + i * (end - start) / (steps - 1) for i in range(steps)]

class GridSearchCandidateGenerator(CandidateGenerator):
    """
    Generates a uniform, deterministic grid of candidates within bounds.
    """
    def generate(self, bounds: OptimizationBounds) -> List[PlanformCandidate]:
        ar_vals = linspace(bounds.min_aspect_ratio, bounds.max_aspect_ratio, bounds.aspect_ratio_steps)
        taper_vals = linspace(bounds.min_taper_ratio, bounds.max_taper_ratio, bounds.taper_ratio_steps)
        sweep_vals = linspace(bounds.min_sweep_deg, bounds.max_sweep_deg, bounds.sweep_steps)
        wl_vals = linspace(bounds.min_wing_loading_kg_m2, bounds.max_wing_loading_kg_m2, bounds.wing_loading_steps)

        candidates = []
        for ar in ar_vals:
            for taper in taper_vals:
                for sweep in sweep_vals:
                    for wl in wl_vals:
                        candidates.append(
                            PlanformCandidate(
                                aspect_ratio=round(ar, 4),
                                taper_ratio=round(taper, 4),
                                sweep_angle_deg=round(sweep, 4),
                                wing_loading_kg_m2=round(wl, 4)
                            )
                        )
        return candidates

class DeterministicRandomCandidateGenerator(CandidateGenerator):
    """
    Generates a reproducible randomized set of candidates within bounds.
    """
    def __init__(self, sample_size: int = 50, seed: int = 42) -> None:
        self.sample_size = sample_size
        self.seed = seed

    def generate(self, bounds: OptimizationBounds) -> List[PlanformCandidate]:
        rng = random.Random(self.seed)
        candidates = []
        for _ in range(self.sample_size):
            ar = rng.uniform(bounds.min_aspect_ratio, bounds.max_aspect_ratio)
            taper = rng.uniform(bounds.min_taper_ratio, bounds.max_taper_ratio)
            sweep = rng.uniform(bounds.min_sweep_deg, bounds.max_sweep_deg)
            wl = rng.uniform(bounds.min_wing_loading_kg_m2, bounds.max_wing_loading_kg_m2)
            candidates.append(
                PlanformCandidate(
                    aspect_ratio=round(ar, 4),
                    taper_ratio=round(taper, 4),
                    sweep_angle_deg=round(sweep, 4),
                    wing_loading_kg_m2=round(wl, 4)
                )
            )
        return candidates
