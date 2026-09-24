"""
ConfigurationConstraints Subsystem

Purpose:
    Defines the `ConfigurationConstraints` domain model representing constraints on multirotor structural architecture.

Role in Architecture:
    `ConfigurationConstraints` specifies min/max rotor counts, coaxial configuration allowance, and motor failure redundancy requirements.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ConfigurationConstraints:
    """
    Multirotor frame configuration constraints model.

    Attributes:
        max_rotors (int): Upper bound on total motor/rotor count (default 8).
        min_rotors (int): Lower bound on total motor/rotor count (default 4).
        allow_coaxial (bool): True if coaxial multirotor frames (Y6, X8) are allowed.
        required_redundancy (str): Motor failure redundancy constraint ('NONE', 'SINGLE', 'DUAL').
        metadata (dict[str, Any]): Additional constraint diagnostic metadata.
    """

    max_rotors: int = 8
    min_rotors: int = 4
    allow_coaxial: bool = True
    required_redundancy: str = "NONE"
    metadata: dict[str, Any] = field(default_factory=dict)
