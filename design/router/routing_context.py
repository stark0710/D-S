"""
RoutingContext Subsystem

Purpose:
    Defines the `RoutingContext` domain model capturing routing dispatch context information.

Role in Architecture:
    `RoutingContext` records selected aircraft type, target engine ID, timestamp, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from backend.design.common.requirements.aircraft_type import AircraftType


def _current_timestamp() -> str:
    """Helper returning current UTC ISO 8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class RoutingContext:
    """
    Routing context information snapshot.

    Attributes:
        selected_aircraft (AircraftType): Target aircraft configuration category.
        selected_engine (str): Identifier of the dispatched design engine.
        timestamp (str): ISO 8601 creation timestamp string.
        metadata (dict[str, Any]): Additional operational metadata.
    """

    selected_aircraft: AircraftType
    selected_engine: str
    timestamp: str = field(default_factory=_current_timestamp)
    metadata: dict[str, Any] = field(default_factory=dict)
