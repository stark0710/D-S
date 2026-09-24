"""
DesignResult Subsystem

Purpose:
    Defines the `DesignResult` domain model representing the output of a DesignStudio execution.

Role in Architecture:
    `DesignResult` encapsulates execution success status, final `DesignContext`, generated `DesignArtifact` list,
    warnings, errors, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.design.common.context.design_context import DesignContext
from backend.design.studio.design_artifact import DesignArtifact


@dataclass(slots=True)
class DesignResult:
    """
    Design studio workflow execution output summary.

    Attributes:
        success (bool): True if design workflow executed successfully; False otherwise.
        final_design_context (DesignContext): Final updated DesignContext instance.
        artifacts (list[DesignArtifact]): Generated engineering design artifacts.
        warnings (list[str]): Non-fatal warnings encountered during design execution.
        errors (list[str]): Fatal or non-fatal execution error messages.
        metadata (dict[str, Any]): Additional execution diagnostic metadata.
    """

    success: bool
    final_design_context: DesignContext
    artifacts: list[DesignArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
