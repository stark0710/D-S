"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Context

Encapsulates requirements, configuration layouts, and specs passed across optimizers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.common.requirements.optimization_priority import OptimizationPriority

@dataclass
class OptimizationContext:
    """
    Holds global mission requirements, aircraft configuration state,
    historical specification updates, and search metadata.
    """
    requirements: Any
    configuration: Any = None
    previous_specifications: Dict[str, Any] = field(default_factory=dict)
    global_constraints: Dict[str, Any] = field(default_factory=dict)
    iteration_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    optimization_priority: OptimizationPriority = OptimizationPriority.BALANCED

    def __post_init__(self) -> None:
        # If optimization_priority was left at default BALANCED, inspect requirements to see if
        # an explicit priority was configured upstream.
        if self.optimization_priority == OptimizationPriority.BALANCED and self.requirements is not None:
            raw_req = getattr(self.requirements, "raw_requirements", None)
            if raw_req and hasattr(raw_req, "optimization_priority"):
                self.optimization_priority = raw_req.optimization_priority
            elif hasattr(self.requirements, "optimization_priority"):
                self.optimization_priority = self.requirements.optimization_priority
            elif hasattr(self.requirements, "mission_requirements") and hasattr(self.requirements.mission_requirements, "optimization_priority"):
                self.optimization_priority = self.requirements.mission_requirements.optimization_priority

