"""
Fixed-Wing Mission Payload Selector Subsystem

Purpose:
    Defines the `PayloadSelector` class and the database of payload records.

Role in Architecture:
    `PayloadSelector` maps target strategy needs to concrete sensors or cargo specifications.
"""

from typing import List, Optional
from backend.design.fixed_wing.payload.payload_requirements import PayloadType


class PayloadRecord:
    """Payload item details."""

    def __init__(
        self,
        name: str,
        payload_type: PayloadType,
        weight_kg: float,
        power_w: float,
        bandwidth_mbps: float,
        dimensions_mm: List[float],  # [L, W, H]
    ) -> None:
        self.name = name
        self.payload_type = payload_type
        self.weight_kg = weight_kg
        self.power_w = power_w
        self.bandwidth_mbps = bandwidth_mbps
        self.dimensions_mm = dimensions_mm


class PayloadSelector:
    """
    Selector class matching payload types to database items.
    """

    _payloads: List[PayloadRecord] = [
        # RGB Cameras
        PayloadRecord("Micro FPV / Action Camera", PayloadType.RGB_CAMERA, 0.08, 3.0, 2.0, [32.0, 32.0, 28.0]),
        PayloadRecord("Compact Mapping Camera", PayloadType.RGB_CAMERA, 0.25, 8.0, 4.0, [65.0, 45.0, 38.0]),
        PayloadRecord("Sony RX1R II (RGB)", PayloadType.RGB_CAMERA, 0.51, 15.0, 5.0, [113.0, 72.0, 74.0]),

        # Specialized Imaging
        PayloadRecord("MicaSense RedEdge (Multispectral)", PayloadType.MULTISPECTRAL, 0.35, 8.0, 2.0, [87.0, 59.0, 45.4]),
        PayloadRecord("FLIR Duo Pro R (Thermal)", PayloadType.THERMAL, 0.22, 12.0, 4.0, [87.0, 82.0, 69.0]),
        PayloadRecord("Velodyne VLP-16 (LiDAR)", PayloadType.LIDAR, 0.83, 10.0, 8.0, [103.0, 103.0, 72.0]),

        # Scientific Instruments
        PayloadRecord("Lightweight Atmospheric Probe", PayloadType.SCIENTIFIC, 0.35, 5.0, 1.0, [120.0, 50.0, 40.0]),
        PayloadRecord("Compact Scientific Sensor Package", PayloadType.SCIENTIFIC, 0.60, 8.0, 2.0, [140.0, 60.0, 50.0]),
        PayloadRecord("Agricultural Spray Tank System", PayloadType.SCIENTIFIC, 1.80, 12.0, 0.5, [250.0, 120.0, 120.0]),

        # Cargo Packages
        PayloadRecord("Lightweight Modular Courier Package", PayloadType.CARGO, 1.00, 0.0, 0.0, [140.0, 80.0, 80.0]),
        PayloadRecord("Standard Cargo Box Package", PayloadType.CARGO, 2.00, 0.0, 0.0, [180.0, 100.0, 100.0]),

        # Environmental Sensors
        PayloadRecord("MetSens Environmental Probe", PayloadType.ENV_SENSORS, 0.15, 2.0, 0.1, [60.0, 40.0, 30.0]),
    ]

    @staticmethod
    def _calculate_cargo_dimensions_mm(weight_kg: float) -> List[float]:
        """
        Calculates realistic cargo package dimensions (L x W x H) in millimeters,
        scaling from a standard courier reference box (2.0 kg -> 180 x 100 x 100 mm).
        """
        ref_weight = 2.0
        ref_dims = [180.0, 100.0, 100.0]
        scale = max(0.05, weight_kg / ref_weight) ** (1.0 / 3.0)
        return [round(d * scale, 1) for d in ref_dims]

    def select_payload(
        self,
        target_type: PayloadType,
        max_weight_kg: float,
        target_weight_kg: Optional[float] = None,
    ) -> PayloadRecord:
        """
        Selects the best database record of the target type or synthesizes a generic cargo representation.

        Args:
            target_type (PayloadType): The requested payload type category.
            max_weight_kg (float): Structural payload weight ceiling.
            target_weight_kg (Optional[float]): Optional target payload mass (defaults to max_weight_kg / 1.05).

        Returns:
            PayloadRecord: Sized and matched payload record.

        Raises:
            ValueError: If components of target_type are missing or physically exceed max_weight_kg.
        """
        # Determine target weight preference
        if target_weight_kg is not None and target_weight_kg > 0.0:
            target_weight = target_weight_kg
        else:
            target_weight = round(max_weight_kg / 1.05, 3) if max_weight_kg > 0.0 else 0.0

        # Special handling for generic cargo / custom parcel representation
        if target_type in (PayloadType.CARGO, PayloadType.CUSTOM):
            # 1. Check for exact or closely matching catalog cargo item
            matching_catalog = [
                p for p in self._payloads
                if p.payload_type == target_type
                and abs(p.weight_kg - target_weight) < 0.05
                and p.weight_kg <= max_weight_kg
            ]
            if matching_catalog:
                return matching_catalog[0]

            # 2. If requested cargo weight is physically feasible within limits, synthesize generic payload
            if 0.0 < target_weight <= max_weight_kg:
                dims = self._calculate_cargo_dimensions_mm(target_weight)
                type_label = "Cargo Package" if target_type == PayloadType.CARGO else "Custom Payload"
                return PayloadRecord(
                    name=f"Generic {type_label} ({target_weight:.2f} kg)",
                    payload_type=target_type,
                    weight_kg=target_weight,
                    power_w=0.0 if target_type == PayloadType.CARGO else 5.0,
                    bandwidth_mbps=0.0 if target_type == PayloadType.CARGO else 1.0,
                    dimensions_mm=dims,
                )
            elif target_weight > max_weight_kg:
                raise ValueError(
                    f"COMPONENT_DATABASE_LIMITATION: Requested {target_type.value} mass of {target_weight:.2f} kg "
                    f"exceeds the maximum allowed structural payload limit of {max_weight_kg:.2f} kg."
                )

        # Standard catalog selection for discrete sensor components
        candidates = [p for p in self._payloads if p.payload_type == target_type and p.weight_kg <= max_weight_kg]
        if not candidates:
            all_of_type = [p for p in self._payloads if p.payload_type == target_type]
            if all_of_type:
                lightest = min(all_of_type, key=lambda p: p.weight_kg)
                raise ValueError(
                    f"COMPONENT_DATABASE_LIMITATION: Lightest available component of type '{target_type.value}' "
                    f"in database weighs {lightest.weight_kg:.2f} kg, which exceeds the maximum allowed "
                    f"structural payload limit of {max_weight_kg:.2f} kg."
                )
            else:
                raise ValueError(
                    f"COMPONENT_DATABASE_LIMITATION: No payload components of type '{target_type.value}' "
                    f"are available in the database."
                )

        # Pick candidate closest to target_weight without exceeding max_weight_kg
        return min(candidates, key=lambda p: abs(p.weight_kg - target_weight))
