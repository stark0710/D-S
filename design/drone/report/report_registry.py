# backend/design/drone/report/report_registry.py
"""Registry for report generation strategies.

The registry allows dynamic discovery and selection of a concrete
:class:`ReportStrategy` implementation by name.
"""

from __future__ import annotations

from typing import Dict, Type

from .report_strategy import ReportStrategy


class ReportStrategyRegistry:
    """Central registry for report strategies.

    Strategies are registered via the ``register`` classmethod.  Retrieval
    returns a *new* instance of the strategy class.
    """

    _registry: Dict[str, Type[ReportStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[ReportStrategy]) -> None:
        """Register a strategy class under a given name.

        Parameters
        ----------
        name: str
            Identifier used to retrieve the strategy (e.g., "executive").
        strategy_cls: Type[ReportStrategy]
            Concrete subclass of :class:`ReportStrategy`.
        """
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> ReportStrategy:
        """Retrieve an instantiated strategy by name.

        Raises
        ------
        KeyError
            If the name is not registered.
        """
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            raise KeyError(f"Report strategy '{name}' not found in registry.")
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Return a list of registered strategy names."""
        return list(cls._registry.keys())
