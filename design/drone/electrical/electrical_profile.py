"""
ElectricalProfile Subsystem

Purpose:
    Defines the `ElectricalProfile` domain model representing multirotor electrical subsystem specifications.

Role in Architecture:
    `ElectricalProfile` encapsulates battery chemistry, cell count S, capacity mAh, discharge C-rating,
    ESC rating, PDB rating, connector type, and main wire AWG.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ElectricalProfile:
    """
    Multirotor electrical subsystem specification profile.

    Attributes:
        battery_chemistry (str): Battery chemistry ('LiPo', 'LiHV', 'Li-Ion').
        cell_count_s (int): Battery cell series count (e.g. 6S).
        capacity_mah (float): Battery capacity in mAh.
        discharge_rating_c (float): Continuous discharge rating in C.
        esc_current_rating_a (float): Continuous ESC current rating per channel in Amperes.
        pdb_current_rating_a (float): Continuous PDB current rating in Amperes.
        connector_type (str): Main battery power connector specification.
        main_wire_awg (int): Main battery lead AWG size.
        metadata (dict[str, Any]): Additional electrical profile metadata.
    """

    battery_chemistry: str
    cell_count_s: int
    capacity_mah: float
    discharge_rating_c: float
    esc_current_rating_a: float
    pdb_current_rating_a: float
    connector_type: str
    main_wire_awg: int
    metadata: dict[str, Any] = field(default_factory=dict)
