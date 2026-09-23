"""
Fixed-Wing Center of Gravity (CG) Optimization Package
"""

from backend.design.fixed_wing.cg.optimization.cg_optimizer import CGOptimizer
from backend.design.fixed_wing.cg.optimization.models import CGSpecification
from backend.design.fixed_wing.cg.optimization.result import CGOptimizationResult

__all__ = [
    "CGOptimizer",
    "CGSpecification",
    "CGOptimizationResult",
]
