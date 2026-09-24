"""
StageRegistry Subsystem

Purpose:
    Defines the `StageRegistry` class responsible for registering and managing reusable `DesignStage` classes.

Role in Architecture:
    `StageRegistry` provides the plugin registry for reusable stage classes.
    It enforces unique stage name registration and enables dynamic discovery of stage implementations.
"""

from backend.design.studio.stages.design_stage import DesignStage


class DuplicateStageRegistrationError(ValueError):
    """Raised when attempting to register a stage class with an already registered stage_name."""
    pass


class StageNotFoundError(KeyError):
    """Raised when looking up a stage class name that is absent from the registry."""
    pass


class StageRegistry:
    """
    Registry for managing reusable DesignStage classes.

    Design Principles:
        - Registry Pattern: Centralized registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom stage steps.
    """

    def __init__(self) -> None:
        """Initializes the StageRegistry."""
        self._stage_classes: dict[str, type[DesignStage]] = {}

    def register_stage(self, stage_class: type[DesignStage]) -> None:
        """
        Registers a reusable stage class.

        Args:
            stage_class (type[DesignStage]): Class implementing DesignStage.

        Raises:
            DuplicateStageRegistrationError: If stage_name is already registered.
        """
        temp_instance = stage_class()
        s_name = temp_instance.stage_name

        if s_name in self._stage_classes:
            existing = self._stage_classes[s_name]
            raise DuplicateStageRegistrationError(
                f"DesignStage with name '{s_name}' is already registered (Existing class: {existing.__name__})."
            )

        self._stage_classes[s_name] = stage_class

    def get_stage_class(self, stage_name: str) -> type[DesignStage]:
        """
        Retrieves a registered stage class by name.

        Args:
            stage_name (str): Stage identifier name.

        Returns:
            type[DesignStage]: Registered stage class.

        Raises:
            StageNotFoundError: If stage_name is absent from registry.
        """
        if stage_name not in self._stage_classes:
            raise StageNotFoundError(f"DesignStage class for '{stage_name}' not found in registry.")
        return self._stage_classes[stage_name]

    def registered_stages(self) -> list[type[DesignStage]]:
        """Returns a list of all registered DesignStage classes."""
        return list(self._stage_classes.values())
