"""
VTOL Electrical Protection Subsystem

Purpose:
    Defines the `FuseSpec` and `ElectricalProtection` classes sizing protective fuses.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class FuseSpec:
    """
    Sized electrical fuse.

    Attributes:
        name (str): Fuse name (e.g. Main battery fuse, ESC 1 fuse).
        fuse_rating_a (float): Sized current capacity in amps.
        blow_delay_ms (float): Sized blow delay in milliseconds.
    """

    name: str
    fuse_rating_a: float
    blow_delay_ms: float


@dataclass(slots=True)
class ElectricalProtection:
    """
    Sized circuit protection systems.

    Attributes:
        fuses (List[FuseSpec]): Sized fuses.
        circuit_breakers (List[str]): Sized automatic circuit breakers.
        has_power_monitoring (bool): True if system telemeters voltage/current levels.
        metadata (Dict[str, Any]): Protection details.
    """

    fuses: List[FuseSpec]
    circuit_breakers: List[str]
    has_power_monitoring: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
