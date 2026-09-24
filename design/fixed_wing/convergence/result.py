"""
Fixed-Wing Aircraft Convergence Result
"""

from typing import Dict, Any, List
from backend.design.fixed_wing.convergence.models import FinalAircraftSpecification


class AircraftConvergenceResult:
    """
    Result container returning converged aircraft configurations and iteration histories.
    """
    def __init__(
        self,
        success: bool,
        message: str,
        final_specification: FinalAircraftSpecification | None = None,
        diagnostics: Dict[str, Any] = None,
    ) -> None:
        self.success = success
        self.message = message
        self.final_specification = final_specification
        self.diagnostics = diagnostics or {}
