"""
Fixed-Wing Companion Computer Selector Subsystem

Purpose:
    Defines the `CompanionComputerSelector` class and SBC database.

Role in Architecture:
    `CompanionComputerSelector` selects companion computers for visual processing.
"""

from typing import List


class CompanionComputerRecord:
    """SBC hardware description."""

    def __init__(self, name: str, weight_g: float, ram_gb: float, power_w: float, ai_tops: float) -> None:
        self.name = name
        self.weight_g = weight_g
        self.ram_gb = ram_gb
        self.power_w = power_w
        self.ai_tops = ai_tops


class CompanionComputerSelector:
    """
    Selector class matching companion processors to AI/Visual navigation needs.
    """

    _computers: List[CompanionComputerRecord] = [
        CompanionComputerRecord("Raspberry Pi 4 Model B", 46, 8.0, 7.5, 0.0),
        CompanionComputerRecord("NVIDIA Jetson Orin Nano", 85, 8.0, 15.0, 40.0),
        CompanionComputerRecord("NVIDIA Jetson Orin NX", 110, 16.0, 25.0, 100.0),
        CompanionComputerRecord("Intel NUC Core i7", 450, 32.0, 45.0, 0.0),
    ]

    def select_companion_computer(self, needs_visual_nav: bool, needs_high_ai: bool) -> CompanionComputerRecord | None:
        if not needs_visual_nav and not needs_high_ai:
            return None

        candidates = self._computers
        if needs_high_ai:
            candidates = [c for c in candidates if c.ai_tops >= 40.0]
        elif needs_visual_nav:
            candidates = [c for c in candidates if c.weight_g <= 120.0]  # keep lightweight on wings

        if not candidates:
            return self._computers[0]

        return min(candidates, key=lambda c: c.weight_g)
