"""
QualityPlan Subsystem

Purpose:
    Defines the `QualityPlan` domain model representing pre-flight and pre-shipment quality assurance tests.

Role in Architecture:
    `QualityPlan` specifies dimensional tolerances, structural static load test metrics, and ESC/electrical current check targets.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class QualityPlan:
    """
    Multirotor Quality Assurance (QA) plan details.

    Attributes:
        dimensional_tolerances (dict[str, str]): Dimensional QA tolerance limits (e.g. wheelbase +/- 2.0mm).
        structural_load_test_n (float): Structural static torque load test limit in N.
        electrical_dielectric_test_v (float): Electrical insulation test target in V.
        metadata (dict[str, Any]): Additional QA metadata.
    """

    dimensional_tolerances: dict[str, str] = field(default_factory=dict)
    structural_load_test_n: float = 100.0
    electrical_dielectric_test_v: float = 500.0
    metadata: dict[str, Any] = field(default_factory=dict)
