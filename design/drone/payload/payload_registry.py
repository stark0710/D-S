"""
PayloadRegistry Subsystem

Purpose:
    Defines the `PayloadRegistry` class responsible for registering and managing multirotor payload strategies.

Role in Architecture:
    `PayloadRegistry` provides the plugin registry for payload integration design strategies.
"""

from backend.design.drone.payload.payload_strategy import PayloadStrategy


class PayloadRegistry:
    """
    Registry for managing PayloadStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom payload strategies.
    """

    def __init__(self) -> None:
        """Initializes PayloadRegistry."""
        self._strategies: dict[str, PayloadStrategy] = {}

    def register_strategy(self, strategy: PayloadStrategy) -> None:
        """Registers a PayloadStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> PayloadStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"PayloadStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[PayloadStrategy]:
        """Returns a list of all registered PayloadStrategy instances."""
        return list(self._strategies.values())
