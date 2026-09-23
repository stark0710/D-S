"""
Fixed-Wing CAD Strategy and Backend Registry Subsystem

Purpose:
    Defines registries for lookup of CAD strategies and backend engines.

Role in Architecture:
    Enables pluggable strategies and backends (CadQuery, OpenCascade, etc.) through registry lookups.
"""

from typing import Dict, Type, Any
from backend.design.fixed_wing.cad.cad_strategy import (
    CADStrategy,
    RapidPrototypeCADStrategy,
    ManufacturingCADStrategy,
    SimulationCADStrategy,
    LightweightCADStrategy,
    ResearchCADStrategy,
    BalancedCADStrategy,
)


class CADStrategyRegistry:
    """
    Registry for CAD generation strategies.
    """

    _registry: Dict[str, Type[CADStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[CADStrategy]) -> None:
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> CADStrategy:
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedCADStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        return list(cls._registry.keys())


class CADBackendRegistry:
    """
    Registry for CAD engine backends (e.g. OpenCascade, CadQuery, FreeCAD).
    """

    _registry: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, backend_instance: Any) -> None:
        cls._registry[name.lower()] = backend_instance

    @classmethod
    def get(cls, name: str) -> Any:
        # Default to a mock/custom backend representation if none is registered
        return cls._registry.get(name.lower(), "custom_cad_backend")

    @classmethod
    def list_backends(cls) -> list[str]:
        return list(cls._registry.keys())


# Pre-register default CAD strategies
CADStrategyRegistry.register("rapid prototype", RapidPrototypeCADStrategy)
CADStrategyRegistry.register("manufacturing", ManufacturingCADStrategy)
CADStrategyRegistry.register("simulation", SimulationCADStrategy)
CADStrategyRegistry.register("lightweight", LightweightCADStrategy)
CADStrategyRegistry.register("research", ResearchCADStrategy)
CADStrategyRegistry.register("balanced", BalancedCADStrategy)

# Pre-register default backends
CADBackendRegistry.register("cadquery", "cadquery_backend_instance")
CADBackendRegistry.register("opencascade", "opencascade_backend_instance")
CADBackendRegistry.register("freecad", "freecad_backend_instance")
CADBackendRegistry.register("custom", "custom_backend_instance")
