"""
VerificationRegistry Subsystem

Purpose:
    Defines the `VerificationRegistry` class responsible for registering and managing multirotor mission verification strategies.

Role in Architecture:
    `VerificationRegistry` provides the plugin registry for mission verification strategies.
"""

from backend.design.drone.verification.verification_strategy import VerificationStrategy


class VerificationRegistry:
    """
    Registry for managing VerificationStrategy instances.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom mission verification strategies.
    """

    def __init__(self) -> None:
        """Initializes VerificationRegistry."""
        self._strategies: dict[str, VerificationStrategy] = {}

    def register_strategy(self, strategy: VerificationStrategy) -> None:
        """Registers a VerificationStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> VerificationStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"VerificationStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[VerificationStrategy]:
        """Returns a list of all registered VerificationStrategy instances."""
        return list(self._strategies.values())
