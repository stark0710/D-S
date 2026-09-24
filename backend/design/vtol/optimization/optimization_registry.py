from typing import Dict, Type
from .optimization_strategy import (
    OptimizationStrategy, NSGA2OptimizationStrategy, GAOptimizationStrategy,
    PSOOptimizationStrategy, BayesianOptimizationStrategy, SimulatedAnnealingStrategy,
    HybridOptimizationStrategy, CustomOptimizationStrategy
)

class OptimizationRegistry:
    """
    Registry mapping optimizer string tags to concrete strategies.
    """
    _registry: Dict[str, Type[OptimizationStrategy]] = {
        "NSGA-II": NSGA2OptimizationStrategy,
        "GA": GAOptimizationStrategy,
        "PSO": PSOOptimizationStrategy,
        "Bayesian": BayesianOptimizationStrategy,
        "Simulated Annealing": SimulatedAnnealingStrategy,
        "Hybrid": HybridOptimizationStrategy,
        "Custom": CustomOptimizationStrategy
    }

    @classmethod
    def get_strategy(cls, optimizer_type: str | None) -> OptimizationStrategy:
        strategy_class = cls._registry.get(optimizer_type or "NSGA-II", NSGA2OptimizationStrategy)
        return strategy_class()
