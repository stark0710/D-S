"""
Exceptions for Fixed-Wing Design Pipeline Orchestrator.
"""

class FixedWingPipelineError(Exception):
    """Base exception for all fixed-wing pipeline errors."""
    pass


class InvalidRequirementsError(FixedWingPipelineError):
    """Raised when incoming requirement model fails validation."""
    pass


class ConfigurationInfeasibleError(FixedWingPipelineError):
    """Raised when no feasible aircraft configuration can be selected."""
    pass


class SizingInfeasibleError(FixedWingPipelineError):
    """Raised when wing, tail, or fuselage sizing fails engineering constraints."""
    pass


class ComponentSelectionError(FixedWingPipelineError):
    """Raised when propulsion, motor, ESC, or battery selection fails."""
    pass


class NonConvergenceError(FixedWingPipelineError):
    """Raised when the multidisciplinary sizing loop fails to converge within max iterations."""
    def __init__(self, message: str, history: list | None = None) -> None:
        super().__init__(message)
        self.history = history or []


class VerificationFailedError(FixedWingPipelineError):
    """Raised when post-design verification checks detect critical compliance failures."""
    pass
