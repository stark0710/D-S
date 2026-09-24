"""
DesignEngineRegistry Subsystem

Purpose:
    Defines the `DesignEngineRegistry` class responsible for registering, validating, and looking up category-specific `DesignEngine` instances.

Role in Architecture:
    `DesignEngineRegistry` provides the plugin registry for Design Studios.
    It enforces unique registrations by engine ID and supported `AircraftType`, enabling dynamic extension without code modifications.
"""

from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.router.design_engine import DesignEngine
from backend.design.router.routing_exception import (
    EngineNotRegisteredError,
    UnsupportedAircraftTypeError,
    DuplicateRegistrationError,
)


class DesignEngineRegistry:
    """
    Registry for managing category-specific DesignEngine implementations.

    Design Principles:
        - Registry Pattern: Centralized registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for future design studios.
    """

    def __init__(self) -> None:
        """Initializes the DesignEngineRegistry."""
        self._engine_id_map: dict[str, DesignEngine] = {}
        self._aircraft_type_map: dict[AircraftType, DesignEngine] = {}

    def register_engine(self, engine: DesignEngine) -> None:
        """
        Registers a new DesignEngine implementation.

        Args:
            engine (DesignEngine): Design engine instance to register.

        Raises:
            DuplicateRegistrationError: If engine_id or any supported aircraft_type is already registered.
        """
        if engine.engine_id in self._engine_id_map:
            existing = self._engine_id_map[engine.engine_id]
            raise DuplicateRegistrationError(
                f"Design engine with ID '{engine.engine_id}' is already registered (Existing: {type(existing).__name__})."
            )

        for atype in engine.supported_aircraft_types:
            if atype in self._aircraft_type_map:
                existing = self._aircraft_type_map[atype]
                raise DuplicateRegistrationError(
                    f"Aircraft category '{atype.value}' already has registered engine '{existing.engine_id}'."
                )

        self._engine_id_map[engine.engine_id] = engine
        for atype in engine.supported_aircraft_types:
            self._aircraft_type_map[atype] = engine

    def get_engine_by_id(self, engine_id: str) -> DesignEngine:
        """
        Retrieves a DesignEngine by its unique string engine ID.

        Args:
            engine_id (str): Unique engine identifier string.

        Returns:
            DesignEngine: Matching design engine instance.

        Raises:
            EngineNotRegisteredError: If engine_id is missing from the registry.
        """
        if engine_id not in self._engine_id_map:
            raise EngineNotRegisteredError(
                f"Design engine with ID '{engine_id}' not found in registry."
            )
        return self._engine_id_map[engine_id]

    def get_engine_by_aircraft_type(self, aircraft_type: AircraftType) -> DesignEngine:
        """
        Retrieves the registered DesignEngine for the specified AircraftType.

        Args:
            aircraft_type (AircraftType): Target aircraft category.

        Returns:
            DesignEngine: Matching design engine instance.

        Raises:
            UnsupportedAircraftTypeError: If no design engine is registered for aircraft_type.
        """
        if aircraft_type not in self._aircraft_type_map:
            raise UnsupportedAircraftTypeError(
                f"No design engine registered for aircraft category '{aircraft_type.value}'."
            )
        return self._aircraft_type_map[aircraft_type]

    def has_engine_for_type(self, aircraft_type: AircraftType) -> bool:
        """Checks whether a design engine is registered for the specified aircraft category."""
        return aircraft_type in self._aircraft_type_map

    def registered_engines(self) -> list[DesignEngine]:
        """Returns a list of all distinct registered DesignEngine instances."""
        return list(self._engine_id_map.values())
