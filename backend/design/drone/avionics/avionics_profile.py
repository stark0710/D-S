"""
AvionicsProfile Subsystem

Purpose:
    Defines the `AvionicsProfile` domain model representing multirotor avionics architecture specifications.

Role in Architecture:
    `AvionicsProfile` encapsulates flight controller model, firmware stack, GNSS model, telemetry model,
    RC receiver model, companion computer model, and camera model.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AvionicsProfile:
    """
    Multirotor avionics subsystem specification profile.

    Attributes:
        flight_controller_model (str): Flight controller hardware model.
        firmware (str): Autopilot firmware stack string.
        gps_model (str): GNSS module specification.
        telemetry_model (str): Telemetry radio module specification.
        receiver_model (str): RC control receiver specification.
        companion_computer_model (str | None): Companion computing platform specification.
        camera_model (str | None): Imaging camera payload specification.
        metadata (dict[str, Any]): Additional avionics metadata.
    """

    flight_controller_model: str
    firmware: str
    gps_model: str
    telemetry_model: str
    receiver_model: str
    companion_computer_model: str | None = None
    camera_model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
