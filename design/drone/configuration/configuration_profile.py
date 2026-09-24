"""
ConfigurationProfile Subsystem

Purpose:
    Defines the `ConfigurationProfile` domain model representing a multirotor frame architecture (e.g. Quad X, Hexacopter, Octocopter, X8).

Role in Architecture:
    `ConfigurationProfile` encapsulates structural multirotor configurations, rotor counts, coaxial flags, advantages, and disadvantages.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ConfigurationProfile:
    """
    Multirotor frame configuration definition.

    Attributes:
        config_type (str): Configuration identifier ('QUAD_X', 'QUAD_PLUS', 'HEXACOPTER', 'Y6', 'OCTOCOPTER', 'X8', 'CUSTOM').
        rotor_count (int): Total motor/propeller rotor count (4, 6, 8).
        coaxial (bool): True if rotors are stacked coaxially; False if planar.
        description (str): Human-readable technical description.
        advantages (list[str]): List of key engineering advantages.
        disadvantages (list[str]): List of key engineering trade-offs/disadvantages.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    config_type: str
    rotor_count: int
    coaxial: bool
    description: str
    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
