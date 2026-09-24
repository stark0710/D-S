"""
Fixed-Wing Payload Sizing Profile Subsystem

Purpose:
    Defines the `PayloadProfile` class, which holds geometric tolerances and packaging margins.

Role in Architecture:
    The profile is used to configure isolation frequencies, cooling scaling parameters,
    and payload CG offsets.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PayloadProfile:
    """
    Configuration profile defining limits and tolerances for payload integration.

    Attributes:
        max_allowable_cg_offset_m (float): Maximum longitudinal offset between payload CG and wing center of pressure (default 0.03m).
        vibration_damping_frequency_hz (float): Target isolator isolation frequency (default 20.0 Hz).
        cooling_margin_factor (float): Safety multiplier for thermal dissipation calculations (default 1.2).
        standard_voltage_v (float): Default DC supply bus for payloads (default 5.0 V).
    """

    max_allowable_cg_offset_m: float = 0.03
    vibration_damping_frequency_hz: float = 20.0
    cooling_margin_factor: float = 1.2
    standard_voltage_v: float = 5.0
