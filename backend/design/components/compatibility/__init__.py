"""
Compatibility package for Torq Wings Design Studio Phase 5.2 Universal Component Selection Framework.
"""

from backend.design.components.compatibility.compatibility_status import CompatibilityStatus
from backend.design.components.compatibility.compatibility_severity import CompatibilitySeverity
from backend.design.components.compatibility.compatibility_issue import CompatibilityIssue
from backend.design.components.compatibility.compatibility_result import CompatibilityResult
from backend.design.components.compatibility.compatibility_rule import (
    CompatibilityRule,
    MotorESCCompatibilityRule,
    MotorPropellerCompatibilityRule,
    BatteryESCCompatibilityRule,
    BatteryMotorCompatibilityRule,
    FramePropellerCompatibilityRule,
)
from backend.design.components.compatibility.compatibility_registry import CompatibilityRegistry
from backend.design.components.compatibility.compatibility_pipeline import CompatibilityPipeline
from backend.design.components.compatibility.compatibility_engine import CompatibilityEngine

__all__ = [
    "CompatibilityStatus",
    "CompatibilitySeverity",
    "CompatibilityIssue",
    "CompatibilityResult",
    "CompatibilityRule",
    "MotorESCCompatibilityRule",
    "MotorPropellerCompatibilityRule",
    "BatteryESCCompatibilityRule",
    "BatteryMotorCompatibilityRule",
    "FramePropellerCompatibilityRule",
    "CompatibilityRegistry",
    "CompatibilityPipeline",
    "CompatibilityEngine",
]
