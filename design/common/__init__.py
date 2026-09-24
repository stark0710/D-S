"""
Common design platform package for Torq Wings Design Studio Phase 5.
"""

from backend.design.common.requirements import (
    MissionType,
    AircraftType,
    TakeoffType,
    LandingType,
    OperatingEnvironment,
    OptimizationPriority,
    DesignMode,
    RequirementModel,
)
from backend.design.common.validation import (
    ValidationSeverity,
    ValidationCode,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    RequirementValidator,
    ValidationPipeline,
)
from backend.design.common.context import (
    DesignStage,
    DesignStatus,
    ContextMetadata,
    ContextSnapshot,
    DesignContext,
    ContextBuilder,
)
from backend.design.common.mission import (
    MissionComplexity,
    MissionConstraints,
    MissionProfile,
    MissionAnalysisResult,
    MissionAnalysisService,
    MissionAnalysisEngine,
    MissionAnalysisError,
    InvalidRequirementError,
)

__all__ = [
    "MissionType",
    "AircraftType",
    "TakeoffType",
    "LandingType",
    "OperatingEnvironment",
    "OptimizationPriority",
    "DesignMode",
    "RequirementModel",
    "ValidationSeverity",
    "ValidationCode",
    "ValidationIssue",
    "ValidationResult",
    "ValidationRule",
    "RequirementValidator",
    "ValidationPipeline",
    "DesignStage",
    "DesignStatus",
    "ContextMetadata",
    "ContextSnapshot",
    "DesignContext",
    "ContextBuilder",
    "MissionComplexity",
    "MissionConstraints",
    "MissionProfile",
    "MissionAnalysisResult",
    "MissionAnalysisService",
    "MissionAnalysisEngine",
    "MissionAnalysisError",
    "InvalidRequirementError",
]
