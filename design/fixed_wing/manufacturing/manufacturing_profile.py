"""
Fixed-Wing Manufacturing Profile Subsystem

Purpose:
    Defines the `ManufacturingProfile` class containing default labor rates and pricing multipliers.

Role in Architecture:
    `ManufacturingProfile` sets pricing factors, sheet metal thicknesses, and quality check rules.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ManufacturingProfile:
    """
    Configuration profile defining financial indices and default overhead rates.

    Attributes:
        hourly_labor_rate (float): Cost of manual fabrication time per hour (default 45.0 USD).
        material_overhead_multiplier (float): Safety multiplier on raw material pricing (default 1.15).
        drawing_sheet_size (str): Standard drawing template format ("A3", "A4").
        qc_inspection_level (str): Strictness level ("Standard", "Aerospace").
    """

    hourly_labor_rate: float = 45.0
    material_overhead_multiplier: float = 1.15
    drawing_sheet_size: str = "A3"
    qc_inspection_level: str = "Standard"
