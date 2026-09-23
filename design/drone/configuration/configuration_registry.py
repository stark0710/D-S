"""
ConfigurationRegistry Subsystem

Purpose:
    Defines the `ConfigurationRegistry` class responsible for registering and managing multirotor configuration ranking strategies.

Role in Architecture:
    `ConfigurationRegistry` provides the plugin registry for configuration ranking strategies.
"""

from backend.design.drone.configuration.configuration_strategy import ConfigurationStrategy


class ConfigurationRegistry:
    """
    Registry for multirotor configuration strategies.

    Design Principles:
        - Registry Pattern: Centralized strategy registration and lookup.
        - Open/Closed Principle: Extensible plugin architecture for custom configuration strategies.
    """

    def __init__(self) -> None:
        """Initializes ConfigurationRegistry."""
        self._strategies: dict[str, ConfigurationStrategy] = {}

    def register_strategy(self, strategy: ConfigurationStrategy) -> None:
        """Registers a ConfigurationStrategy."""
        self._strategies[strategy.strategy_name] = strategy

    def get_strategy(self, strategy_name: str) -> ConfigurationStrategy:
        """Retrieves a registered strategy by name."""
        if strategy_name not in self._strategies:
            raise KeyError(f"ConfigurationStrategy '{strategy_name}' is not registered.")
        return self._strategies[strategy_name]

    def registered_strategies(self) -> list[ConfigurationStrategy]:
        """Returns a list of all registered ConfigurationStrategy instances."""
        return list(self._strategies.values())
