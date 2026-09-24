"""
Stages package for Torq Wings Design Studio Phase 5.3 Universal Aircraft Design Stage Library.
"""

from backend.design.studio.stages.stage_category import StageCategory
from backend.design.studio.stages.stage_context import StageContext
from backend.design.studio.stages.stage_result import StageResult
from backend.design.studio.stages.design_stage import DesignStage
from backend.design.studio.stages.stage_validator import StageValidator, StageValidationError
from backend.design.studio.stages.stage_registry import (
    StageRegistry,
    DuplicateStageRegistrationError,
    StageNotFoundError,
)
from backend.design.studio.stages.stage_factory import StageFactory

__all__ = [
    "StageCategory",
    "StageContext",
    "StageResult",
    "DesignStage",
    "StageValidator",
    "StageValidationError",
    "StageRegistry",
    "DuplicateStageRegistrationError",
    "StageNotFoundError",
    "StageFactory",
]
