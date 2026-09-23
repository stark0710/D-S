"""
Fixed-Wing Payload Power Interface Subsystem

Purpose:
    Defines the `PayloadPowerInterface` class representing electrical supply connections.

Role in Architecture:
    `PayloadPowerInterface` holds details on continuous power draw, current, and regulator styles.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PayloadPowerInterface:
    """
    Electrical interface configuration.

    Attributes:
        voltage_v (float): Voltage supplied to the payload (e.g. 5V, 12V).
        max_current_a (float): Sized current draw capacity in Amps.
        connector_type (str): Fastener plug (e.g. JST-GH, XT30).
        regulator_required (bool): Flag indicating if a dedicated BEC is needed.
        power_draw_w (float): Sized continuous wattage.
    """

    voltage_v: float
    max_current_a: float
    connector_type: str
    regulator_required: bool
    power_draw_w: float
