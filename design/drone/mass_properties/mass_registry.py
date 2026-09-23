"""
MassRegistry Subsystem

Purpose:
    Defines the `MassRegistry` class responsible for registering mass calculation extensions.

Role in Architecture:
    `MassRegistry` provides the plugin registry for custom mass and CG analysis calculation extensions.
"""

from typing import Any


class MassRegistry:
    """
    Registry for managing mass property analysis extensions.

    Design Principles:
        - Registry Pattern: Centralized calculation extension registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom mass analysis algorithms.
    """

    def __init__(self) -> None:
        """Initializes MassRegistry."""
        self._calculators: dict[str, Any] = {}

    def register_calculator(self, name: str, calculator: Any) -> None:
        """Registers a mass calculation service."""
        self._calculators[name] = calculator

    def get_calculator(self, name: str) -> Any:
        """Retrieves a registered calculation service by name."""
        if name not in self._calculators:
            raise KeyError(f"Mass calculation service '{name}' is not registered.")
        return self._calculators[name]
