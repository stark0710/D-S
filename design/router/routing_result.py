"""
RoutingResult Subsystem

Purpose:
    Defines the `RoutingResult` domain model representing the output of a router dispatch operation.

Role in Architecture:
    `RoutingResult` stores status, selected engine ID, diagnostic message, and routing execution metadata.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RoutingResult:
    """
    Diagnostic output returned by DesignEngineRouter.

    Attributes:
        selected_engine (str): Identifier of the resolved design engine.
        routing_success (bool): True if routing successfully resolved and dispatched; False otherwise.
        message (str): Diagnostic explanation message.
        metadata (dict[str, Any]): Additional execution metadata.
    """

    selected_engine: str
    routing_success: bool
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
