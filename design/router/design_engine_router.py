"""
DesignEngineRouter Subsystem

Purpose:
    Defines the `DesignEngineRouter` class responsible for resolving and dispatching the user's selected aircraft category to the appropriate Design Studio.

Role in Architecture:
    `DesignEngineRouter` acts as the single point of entry into category-specific Design Studios.
    It reads `selected_aircraft_type` from `DesignContext`, resolves the matching `DesignEngine` from `DesignEngineRegistry`,
    updates context fields, advances `DesignStage`, creates a milestone snapshot, and returns the updated `DesignContext`.
"""

from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.router.design_engine_registry import DesignEngineRegistry
from backend.design.router.routing_exception import UnsupportedAircraftTypeError


class DesignEngineRouter:
    """
    Router for dispatching DesignContext to category-specific Design Studio engines.

    Design Principles:
        - Single Responsibility Principle: Routing dispatch and workflow stage advancement only.
        - Dependency Injection: Injects `DesignEngineRegistry` collaborator.
        - Non-Engine-Logic: Contains no sizing algorithms or aerodynamic calculations.
    """

    def __init__(self, registry: DesignEngineRegistry | None = None) -> None:
        """
        Initializes the DesignEngineRouter.

        Args:
            registry (DesignEngineRegistry | None): Injected registry instance. Defaults to new registry if None.
        """
        self._registry: DesignEngineRegistry = registry if registry else DesignEngineRegistry()

    @property
    def registry(self) -> DesignEngineRegistry:
        """Returns the underlying DesignEngineRegistry instance."""
        return self._registry

    def route(self, context: DesignContext) -> DesignContext:
        """
        Routes the provided DesignContext to the appropriate Design Studio.

        Args:
            context (DesignContext): Target design context to route.

        Returns:
            DesignContext: Updated design context containing selected engine ID and updated workflow stage.

        Raises:
            UnsupportedAircraftTypeError: If no aircraft type is specified or no registered engine supports it.
        """
        # Resolve selected aircraft category
        aircraft_type = context.selected_aircraft_type
        if aircraft_type is None:
            aircraft_type = context.requirement_model.aircraft_type

        if aircraft_type is None:
            raise UnsupportedAircraftTypeError(
                "Cannot route design engine: No target aircraft type specified in DesignContext."
            )

        # Lookup registered engine
        engine = self._registry.get_engine_by_aircraft_type(aircraft_type)

        # Map target workflow stage
        target_stage = self._resolve_target_stage(aircraft_type)

        # Update DesignContext
        context.selected_aircraft_type = aircraft_type
        context.selected_design_engine = engine.engine_id
        context.update_stage(
            stage=target_stage,
            status=DesignStatus.IN_PROGRESS,
            snapshot_summary=f"DesignEngineRouter successfully dispatched context to engine '{engine.engine_id}' for category {aircraft_type.value}."
        )

        return context

    def _resolve_target_stage(self, aircraft_type: AircraftType) -> DesignStage:
        """Maps AircraftType to target DesignStage."""
        if aircraft_type in (AircraftType.QUADCOPTER, AircraftType.HEXACOPTER, AircraftType.OCTOCOPTER):
            return DesignStage.DRONE_DESIGN
        elif aircraft_type == AircraftType.FIXED_WING:
            return DesignStage.FIXED_WING_DESIGN
        elif aircraft_type == AircraftType.VTOL:
            return DesignStage.VTOL_DESIGN
        else:
            return DesignStage.DESIGN_ROUTING
