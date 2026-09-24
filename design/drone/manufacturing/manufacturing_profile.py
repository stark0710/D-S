"""
ManufacturingProfile Subsystem

Purpose:
    Defines the `ManufacturingProfile` domain model representing production run settings.

Role in Architecture:
    `ManufacturingProfile` specifies target batch size, target production method, and assembly location details.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ManufacturingProfile:
    """
    Multirotor manufacturing run profile.

    Attributes:
        batch_size (int): Target production batch size (1 for prototype, >=100 for production).
        facility_name (str): Sourcing assembly workshop facility name.
        sourcing_strategy (str): Parts sourcing model ('LOCAL_DISTRIBUTED', 'CENTRALIZED_FABRICATION').
        metadata (dict[str, Any]): Additional profile metadata.
    """

    batch_size: int = 1
    facility_name: str = "Torq Wings Prototyping Lab"
    sourcing_strategy: str = "LOCAL_DISTRIBUTED"
    metadata: dict[str, Any] = field(default_factory=dict)
