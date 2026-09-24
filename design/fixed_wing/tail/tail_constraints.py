"""
Fixed-Wing Tail Sizing Constraints Subsystem

Purpose:
    Defines the `TailConstraints` class to hold physical bounds.

Role in Architecture:
    `TailConstraints` collects target volume boundaries and allowed layout configurations.
"""

from dataclasses import dataclass, field
from typing import List
from backend.design.fixed_wing.tail.tail_requirements import TailConfigType


@dataclass(slots=True)
class TailConstraints:
    """
    Sizing bounds restricting tail geometry, volume coefficients, and layout compatibility.

    Attributes:
        allowed_styles (List[TailConfigType]): Styles allowed by strategy.
        min_v_h (float): Minimum horizontal tail volume coefficient.
        max_v_h (float): Maximum horizontal tail volume coefficient.
        min_v_v (float): Minimum vertical tail volume coefficient.
        max_v_v (float): Maximum vertical tail volume coefficient.
        max_tail_span_m (float | None): Maximum horizontal tail width constraint.
    """

    allowed_styles: List[TailConfigType] = field(default_factory=list)
    min_v_h: float = 0.3
    max_v_h: float = 1.0
    min_v_v: float = 0.02
    max_v_v: float = 0.10
    max_tail_span_m: float | None = None
