"""
ContextBuilder Subsystem

Purpose:
    Defines the `ContextBuilder` class providing factory methods to construct `DesignContext` objects.

Role in Architecture:
    `ContextBuilder` acts as the builder/factory for `DesignContext` instances.
    It initializes metadata, sets initial stages, and creates baseline snapshots without performing engineering calculations or validations.
"""

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.common.context.context_metadata import ContextMetadata
from backend.design.common.context.design_context import DesignContext


class ContextBuilder:
    """
    Factory builder for DesignContext instances.

    Design Principles:
        - Single Responsibility Principle: Context object instantiation and initialization only.
        - Factory Pattern: Encapsulates creation logic for clean, consistent DesignContext objects.
    """

    @staticmethod
    def create_context(
        requirements: RequirementModel,
        session_id: str = "",
        notes: str = ""
    ) -> DesignContext:
        """
        Constructs a new DesignContext initialized from a RequirementModel.

        Args:
            requirements (RequirementModel): Input requirement model.
            session_id (str): Optional user session identifier.
            notes (str): Optional operational notes.

        Returns:
            DesignContext: Initialized design context object with baseline snapshot.
        """
        metadata = ContextMetadata(session_id=session_id, notes=notes)
        context = DesignContext(
            requirement_model=requirements,
            selected_aircraft_type=requirements.aircraft_type,
            current_stage=DesignStage.REQUIREMENT_COLLECTION,
            current_status=DesignStatus.CREATED,
            metadata=metadata
        )
        context.add_snapshot("DesignContext initialized from RequirementModel.")
        return context
