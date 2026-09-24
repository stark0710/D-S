"""
InspectionPlan Subsystem

Purpose:
    Defines the `InspectionPlan` domain model representing assembly verification inspection checklists.

Role in Architecture:
    `InspectionPlan` provides checklists for visual frame checks, electrical continuity checks, motor spin/rotation checks, and pre-flight sensor checks.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class InspectionPlan:
    """
    Multirotor assembly inspection plan details.

    Attributes:
        visual_checklist (list[str]): Visual frame check checklist items.
        electrical_checklist (list[str]): Continuity, voltage polarity check items.
        mechanical_checklist (list[str]): Motor mounts, fastener torque check items.
        preflight_checklist (list[str]): Pre-flight accelerometer/IMU, GPS lock, telemetry check items.
        metadata (dict[str, Any]): Additional inspection metadata.
    """

    visual_checklist: list[str] = field(default_factory=list)
    electrical_checklist: list[str] = field(default_factory=list)
    mechanical_checklist: list[str] = field(default_factory=list)
    preflight_checklist: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
