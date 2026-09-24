"""
Fixed-Wing Design Pipeline Package.
"""

from backend.design.fixed_wing.pipeline.fixed_wing_pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.pipeline.pipeline_result import FixedWingDesignResult, PipelineStatus
from backend.design.fixed_wing.pipeline.convergence import (
    ConvergenceEvaluator,
    IterationRecord,
    DEFAULT_CONVERGENCE_TOLERANCE,
    DEFAULT_MAX_ITERATIONS,
)
from backend.design.fixed_wing.pipeline.exceptions import (
    FixedWingPipelineError,
    InvalidRequirementsError,
    ConfigurationInfeasibleError,
    SizingInfeasibleError,
    ComponentSelectionError,
    NonConvergenceError,
    VerificationFailedError,
)

__all__ = [
    "FixedWingDesignPipeline",
    "FixedWingPipelineContext",
    "FixedWingDesignResult",
    "PipelineStatus",
    "ConvergenceEvaluator",
    "IterationRecord",
    "DEFAULT_CONVERGENCE_TOLERANCE",
    "DEFAULT_MAX_ITERATIONS",
    "FixedWingPipelineError",
    "InvalidRequirementsError",
    "ConfigurationInfeasibleError",
    "SizingInfeasibleError",
    "ComponentSelectionError",
    "NonConvergenceError",
    "VerificationFailedError",
]
