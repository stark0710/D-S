"""
Fixed-Wing Avionics Communication Analysis Subsystem

Purpose:
    Defines the `CommunicationAnalysis` class.

Role in Architecture:
    `CommunicationAnalysis` evaluates maximum range, data link bandwidth, and failsafe safety triggers.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class CommunicationAnalysis:
    """
    Radio communication link budget metrics.

    Attributes:
        max_range_km (float): Sized max telemetry range.
        bandwidth_kbps (float): Maximum data transfer rate.
        redundancy_enabled (bool): Flag indicating backup RC link (e.g. Crossfire + SiK).
        failsafe_trigger_delay_s (float): Timeout before Return-to-Launch triggers on link loss.
        metadata (Dict[str, Any]): Bandwidth and frequencies.
    """

    max_range_km: float
    bandwidth_kbps: float
    redundancy_enabled: bool
    failsafe_trigger_delay_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)
