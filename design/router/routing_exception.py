"""
RoutingException Subsystem

Purpose:
    Defines exception classes for the Design Engine Routing Framework.

Role in Architecture:
    `RoutingException` and its subclasses handle registry lookup failures, duplicate registrations,
    and unsupported aircraft category routing errors.
"""


class RoutingException(ValueError):
    """Base exception class for Design Engine Router errors."""
    pass


class EngineNotRegisteredError(RoutingException, KeyError):
    """Raised when looking up an engine ID that is absent from the registry."""
    pass


class UnsupportedAircraftTypeError(RoutingException, KeyError):
    """Raised when routing an aircraft category for which no design engine is registered."""
    pass


class RoutingFailureError(RoutingException):
    """Raised when a routing invocation fails during execution."""
    pass


class DuplicateRegistrationError(RoutingException):
    """Raised when attempting to register a design engine with an already registered ID or aircraft type."""
    pass
