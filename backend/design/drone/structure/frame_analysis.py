"""
FrameAnalysis Subsystem

Purpose:
    Defines the `FrameAnalysis` class responsible for multirotor structural calculations.

Role in Architecture:
    `FrameAnalysis` performs structural engineering sizing: calculates required wheelbase, arm length,
    max propeller diameter clearance, center-plate volume, and bare frame weight estimates.
"""

import math


class FrameAnalysis:
    """
    Structural sizing analysis engine for multirotor airframes.

    Design Principles:
        - Single Responsibility Principle: Multirotor frame geometric sizing and weight estimation only.
    """

    def calculate_wheelbase(self, rotor_count: int, estimated_auw_kg: float, coaxial: bool = False) -> float:
        """
        Calculates required motor-to-motor wheelbase in mm.

        Args:
            rotor_count (int): Total rotor count (4, 6, 8).
            estimated_auw_kg (float): Estimated All-Up Weight in kg.
            coaxial (bool): True if coaxial frame.

        Returns:
            float: Wheelbase in mm.
        """
        # Sizing heuristic: heavier drones need larger propellers, requiring larger wheelbase
        base_wb = 350.0
        if estimated_auw_kg > 15.0:
            base_wb = 1200.0
        elif estimated_auw_kg > 8.0:
            base_wb = 960.0
        elif estimated_auw_kg > 4.0:
            base_wb = 680.0
        elif estimated_auw_kg > 2.0:
            base_wb = 550.0

        if coaxial:
            base_wb *= 0.85  # Coaxial frames have smaller arm count footprint

        return round(base_wb, 1)

    def calculate_arm_length(self, wheelbase_mm: float, rotor_count: int, coaxial: bool = False) -> float:
        """
        Calculates individual arm length from center to motor mount.

        Args:
            wheelbase_mm (float): Motor-to-motor wheelbase in mm.
            rotor_count (int): Total rotor count.
            coaxial (bool): True if coaxial frame.

        Returns:
            float: Arm length in mm.
        """
        return round(wheelbase_mm / 2.0, 1)

    def calculate_max_propeller_inch(self, wheelbase_mm: float, rotor_count: int, coaxial: bool = False) -> float:
        """
        Calculates maximum allowed propeller diameter in inches without blade overlap.

        Args:
            wheelbase_mm (float): Wheelbase in mm.
            rotor_count (int): Total rotor count.
            coaxial (bool): True if coaxial frame.

        Returns:
            float: Propeller diameter in inches.
        """
        effective_arms = rotor_count // 2 if coaxial else rotor_count
        angle_rad = (2 * math.pi) / effective_arms
        # Chord distance between adjacent motor locations
        max_prop_mm = wheelbase_mm * math.sin(angle_rad / 2.0) * 0.90  # 10% tip clearance
        max_prop_inch = max_prop_mm / 25.4
        return round(max_prop_inch, 1)

    def estimate_frame_weight(self, wheelbase_mm: float, rotor_count: int, heavy_duty: bool = False) -> float:
        """
        Estimates total bare frame weight in grams.

        Args:
            wheelbase_mm (float): Wheelbase in mm.
            rotor_count (int): Total rotor count.
            heavy_duty (bool): True if industrial heavy-duty frame.

        Returns:
            float: Estimated frame weight in grams.
        """
        base_g = (wheelbase_mm ** 1.35) * 0.12
        if heavy_duty:
            base_g *= 1.35
        return round(base_g, 1)
