"""
Fixed-Wing Tail Sizing Profile Subsystem

Purpose:
    Defines the `TailProfile` class, which holds horizontal and vertical volume coefficient limits.

Role in Architecture:
    The profile allows custom tuning of target horizontal/vertical tail volume stability limits
    and control surface boundary parameters.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class TailProfile:
    """
    Configuration profile defining limits and stability parameters for tail sizing.

    Attributes:
        min_v_h (float): Minimum acceptable horizontal tail volume coefficient (default 0.3).
        max_v_h (float): Maximum acceptable horizontal tail volume coefficient (default 1.0).
        min_v_v (float): Minimum acceptable vertical tail volume coefficient (default 0.02).
        max_v_v (float): Maximum acceptable vertical tail volume coefficient (default 0.10).
        default_tail_arm_ratio (float): Default ratio of tail arm to wingspan (l_t / b) (default 0.6).
    """

    min_v_h: float = 0.3
    max_v_h: float = 1.0
    min_v_v: float = 0.02
    max_v_v: float = 0.10
    default_tail_arm_ratio: float = 0.6
