"""
DesignContext Subsystem

Purpose:
    Defines the `DesignContext` domain model, which serves as the canonical shared state object across all design engines.

Role in Architecture:
    `DesignContext` carries the complete state of an aircraft design process as it moves through requirement collection,
    validation, mission analysis, category recommendation, design studio sizing, optimization, and reporting.
    It contains no business calculations or recommendation logic; it stores state only.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.validation.validation_result import ValidationResult
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.common.context.context_metadata import ContextMetadata
from backend.design.common.context.context_snapshot import ContextSnapshot


@dataclass(slots=True)
class DesignContext:
    """
    Canonical shared state object for Torq Wings AI Aircraft Design Platform.

    Attributes:
        requirement_model (RequirementModel): Input requirement model object.
        validation_result (ValidationResult | None): Requirement validation results, if executed.
        mission_profile (Any | None): Mission physics summary object produced by Mission Analysis Engine.
        vehicle_recommendations (Any | None): Category recommendation report produced by Vehicle Recommendation Engine.
        selected_aircraft_type (AircraftType | None): Approved or specified target aircraft type.
        selected_design_engine (str | None): Identifier of the dispatched design studio engine.
        current_stage (DesignStage): Current workflow lifecycle stage.
        current_status (DesignStatus): Current stage execution status.
        design_data (dict[str, Any]): Intermediate or finalized sizing data dictionary.
        snapshots (list[ContextSnapshot]): Immutable audit trail of completed stage snapshots.
        metadata (ContextMetadata): Administrative session and version metadata.
    """

    requirement_model: RequirementModel
    validation_result: ValidationResult | None = None
    mission_profile: Any | None = None
    vehicle_recommendations: Any | None = None
    selected_aircraft_type: AircraftType | None = None
    selected_design_engine: str | None = None
    current_stage: DesignStage = DesignStage.REQUIREMENT_COLLECTION
    current_status: DesignStatus = DesignStatus.CREATED
    design_data: dict[str, Any] = field(default_factory=dict)
    snapshots: list[ContextSnapshot] = field(default_factory=list)
    metadata: ContextMetadata = field(default_factory=ContextMetadata)

    def add_snapshot(self, summary: str) -> None:
        """
        Creates and appends an immutable ContextSnapshot for the current stage and status.

        Args:
            summary (str): Brief description of the milestone achieved.
        """
        snapshot = ContextSnapshot(
            stage=self.current_stage,
            status=self.current_status,
            summary=summary
        )
        self.snapshots.append(snapshot)

    def update_stage(
        self,
        stage: DesignStage,
        status: DesignStatus = DesignStatus.IN_PROGRESS,
        snapshot_summary: str | None = None
    ) -> None:
        """
        Updates the current workflow stage and status, updating metadata timestamps.

        Args:
            stage (DesignStage): New workflow stage.
            status (DesignStatus): New stage execution status (default IN_PROGRESS).
            snapshot_summary (str | None): Optional summary text to create a snapshot upon stage update.
        """
        self.current_stage = stage
        self.current_status = status
        self.metadata.updated_at = datetime.now(timezone.utc).isoformat()

        if snapshot_summary:
            self.add_snapshot(snapshot_summary)
