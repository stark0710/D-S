"""
Fixed-Wing Mass Properties Optimization Result container
"""

from typing import Dict, Any, List
from backend.design.common.optimization.optimization_result import OptimizationResult
from backend.design.fixed_wing.mass_properties.optimization.models import MassPropertiesSpecification


class MassPropertiesOptimizationResult(OptimizationResult):
    """
    Result container representing the selected weight build-up specification.
    """
    def __init__(
        self,
        winning_candidate: Any,
        generated_specification: MassPropertiesSpecification | None,
        success: bool,
        message: str,
        evaluated_count: int,
        feasible_count: int,
        history: List[Any] = None,
        rejected_summary: Dict[str, Any] = None,
        execution_time_seconds: float = 0.0,
        iteration_count: int = 0,
        diagnostics: Dict[str, Any] = None,
    ) -> None:
        super().__init__(
            winning_candidate=winning_candidate,
            generated_specification=generated_specification,
            success=success,
            message=message,
            evaluated_count=evaluated_count,
            feasible_count=feasible_count,
            history=history or [],
            rejected_summary=rejected_summary or {},
            execution_time_seconds=execution_time_seconds,
            iteration_count=iteration_count,
            diagnostics=diagnostics or {},
        )
