"""
StageContext Subsystem

Purpose:
    Defines the `StageContext` domain model representing execution context passed to a `DesignStage`.

Role in Architecture:
    `StageContext` encapsulates the `DesignContext`, current stage identifier, previous stage identifier,
    next stage identifier, and execution metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.context.design_context import DesignContext


@dataclass(slots=True)
class StageContext:
    """
    Execution context for a single DesignStage step.

    Attributes:
        design_context (DesignContext): Input DesignContext state object.
        current_stage (str): Name of the stage currently executing.
        previous_stage (str | None): Name of the previously executed stage step.
        next_stage (str | None): Name of the upcoming stage step.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    design_context: DesignContext
    current_stage: str
    previous_stage: str | None = None
    next_stage: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
