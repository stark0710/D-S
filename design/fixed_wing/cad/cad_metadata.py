"""
Fixed-Wing CAD Metadata Subsystem

Purpose:
    Defines the `CADMetadata` dataclass representing execution stats.

Role in Architecture:
    `CADMetadata` carries file sizes, time taken to build, and volume stats.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict


@dataclass(slots=True)
class CADMetadata:
    """
    Metadata summarizing the generated 3D CAD characteristics.

    Attributes:
        software_version (str): Code version of the generator engine.
        generating_backend (str): Backend selection ("CadQuery", "OpenCascade").
        generation_time_ms (float): elapsed time during 3D model generation.
        bounding_box_dimensions (Tuple[float, float, float]): Bounding box size (length, width, height) in meters.
        volume_m3 (float): Total geometric solid volume of the aircraft.
        mass_estimate_kg (float): Sized mass estimate.
        backend_metadata (Dict[str, str]): Specific backend diagnostics.
    """

    software_version: str
    generating_backend: str
    generation_time_ms: float
    bounding_box_dimensions: Tuple[float, float, float]
    volume_m3: float
    mass_estimate_kg: float
    backend_metadata: Dict[str, str] = field(default_factory=dict)
