"""
Router package for Torq Wings Design Studio Phase 5.1 Common Design Platform.
"""

from backend.design.router.design_engine import DesignEngine
from backend.design.router.routing_result import RoutingResult
from backend.design.router.routing_context import RoutingContext
from backend.design.router.routing_exception import (
    RoutingException,
    EngineNotRegisteredError,
    UnsupportedAircraftTypeError,
    RoutingFailureError,
    DuplicateRegistrationError,
)
from backend.design.router.design_engine_registry import DesignEngineRegistry
from backend.design.router.design_engine_router import DesignEngineRouter

__all__ = [
    "DesignEngine",
    "RoutingResult",
    "RoutingContext",
    "RoutingException",
    "EngineNotRegisteredError",
    "UnsupportedAircraftTypeError",
    "RoutingFailureError",
    "DuplicateRegistrationError",
    "DesignEngineRegistry",
    "DesignEngineRouter",
]
