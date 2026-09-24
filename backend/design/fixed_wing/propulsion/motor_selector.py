"""
Fixed-Wing Brushless Motor Selector Subsystem

Purpose:
    Defines the `MotorSelector` class and motor records for Electric propulsion sizing.

Role in Architecture:
    `MotorSelector` matches target power requirements (Watts) and thrust limits to brushless DC motors.
"""

from typing import Dict, List


class MotorRecord:
    """Brushless DC motor definition."""

    def __init__(self, name: str, kv: float, weight_g: float, max_power_w: float, nominal_voltage_v: float) -> None:
        self.name = name
        self.kv = kv
        self.weight_g = weight_g
        self.max_power_w = max_power_w
        self.nominal_voltage_v = nominal_voltage_v


class MotorSelector:
    """
    Selector class matching target power requirements to brushless DC motors.
    """

    _motors: List[MotorRecord] = [
        MotorRecord("SunnySky X2216", 1100, 72, 380, 11.1),      # 3S
        MotorRecord("SunnySky X2820", 800, 140, 600, 14.8),      # 4S
        MotorRecord("T-Motor AT3520", 560, 210, 950, 22.2),      # 6S
        MotorRecord("T-Motor AT4120", 400, 310, 1400, 22.2),     # 6S
        MotorRecord("T-Motor MN5008", 340, 140, 700, 22.2),      # 6S (Endurance)
        MotorRecord("T-Motor U8 Lite", 190, 240, 1000, 44.4),    # 12S (Heavy Cargo)
        MotorRecord("KDE Direct 7215XF", 135, 620, 3400, 44.4),  # 12S (Extreme Lift)
    ]

    def select_best_motor(self, target_power_w: float, mission_category: str) -> MotorRecord:
        """
        Finds the smallest motor that can safely sustain the target power with efficiency.
        """
        # For Long Endurance, prioritize high efficiency (lower KV at higher voltage)
        if "Endurance" in mission_category:
            candidates = [m for m in self._motors if m.max_power_w >= target_power_w and m.kv <= 850]
            if candidates:
                return min(candidates, key=lambda m: m.weight_g)

        # Standard search for smallest weight exceeding max power
        candidates = [m for m in self._motors if m.max_power_w >= target_power_w]
        if not candidates:
            # Fallback to the largest KDE motor
            return self._motors[-1]

        return min(candidates, key=lambda m: m.weight_g)
