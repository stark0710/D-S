"""
StageFactory Subsystem

Purpose:
    Defines the `StageFactory` class responsible for instantiating `DesignStage` instances from `StageRegistry`.

Role in Architecture:
    `StageFactory` implements the Factory Pattern for stage creation.
    It supports Dependency Injection and keyword argument passing when creating stage instances.
"""

from typing import Any
from backend.design.studio.stages.design_stage import DesignStage
from backend.design.studio.stages.stage_registry import StageRegistry


class StageFactory:
    """
    Factory for instantiating DesignStage instances.

    Design Principles:
        - Factory Pattern: Encapsulates stage creation logic.
        - Dependency Injection: Injects `StageRegistry` collaborator.
    """

    def __init__(self, registry: StageRegistry | None = None) -> None:
        """
        Initializes the StageFactory.

        Args:
            registry (StageRegistry | None): Injected StageRegistry instance.
        """
        self._registry: StageRegistry = registry if registry else StageRegistry()

    @property
    def registry(self) -> StageRegistry:
        """Returns the underlying StageRegistry."""
        return self._registry

    def create_stage(self, stage_name: str, **kwargs: Any) -> DesignStage:
        """
        Instantiates a DesignStage instance by name.

        Args:
            stage_name (str): Registered stage name.
            **kwargs (Any): Arguments passed to the stage constructor.

        Returns:
            DesignStage: Instantiated design stage object.
        """
        stage_cls = self._registry.get_stage_class(stage_name)
        return stage_cls(**kwargs)
