"""
PayloadVibrationAnalysis Subsystem

Purpose:
    Defines the `PayloadVibrationAnalysis` class and `PayloadVibrationAnalysisResult` dataclass for payload vibration isolation calculations.

Role in Architecture:
    `PayloadVibrationAnalysis` calculates vibration isolation natural frequency in Hz, recommended damper durometer rating,
    and vibration attenuation in dB to prevent camera jello or sensor noise.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PayloadVibrationAnalysisResult:
    """
    Multirotor payload vibration isolation output model.

    Attributes:
        isolation_frequency_hz (float): Target vibration isolation cutoff frequency in Hz.
        damper_durometer_rating (str): Recommended silicone damper Shore hardness rating (e.g. '30A Soft', '40A Medium').
        vibration_attenuation_db (float): Estimated high-frequency motor vibration attenuation in dB.
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    isolation_frequency_hz: float
    damper_durometer_rating: str
    vibration_attenuation_db: float
    metadata: dict[str, Any] = field(default_factory=dict)


class PayloadVibrationAnalysis:
    """
    Analysis service for payload anti-vibration damping physics.

    Design Principles:
        - Single Responsibility Principle: Vibration isolation frequency and damper hardness selection only.
    """

    def analyze_vibration(
        self,
        payload_mass_kg: float,
        sensitive_imaging: bool = True
    ) -> PayloadVibrationAnalysisResult:
        """
        Calculates vibration isolation natural frequency and damper durometer rating.

        Args:
            payload_mass_kg (float): Payload mass in kg.
            sensitive_imaging (bool): True if sensitive optical imaging payload.

        Returns:
            PayloadVibrationAnalysisResult: Computed vibration analysis output.
        """
        if payload_mass_kg > 4.0:
            durometer = "60A Firm"
            iso_freq = 18.0
            attenuation = -24.0
        elif payload_mass_kg > 1.5:
            durometer = "45A Medium"
            iso_freq = 14.0
            attenuation = -28.0
        else:
            durometer = "30A Soft"
            iso_freq = 10.0
            attenuation = -32.0

        return PayloadVibrationAnalysisResult(
            isolation_frequency_hz=iso_freq,
            damper_durometer_rating=durometer,
            vibration_attenuation_db=attenuation
        )
