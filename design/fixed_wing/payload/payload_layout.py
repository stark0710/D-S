"""
Fixed-Wing Payload Layout Subsystem

Purpose:
    Defines the `PayloadLayout` class representing geometric placement and orientation.

Role in Architecture:
    `PayloadLayout` holds coordinate positioning (longitudinal from nose) and optical alignment fields.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class PayloadLayout:
    """
    Physical placement layout of the payload inside the fuselage.

    Attributes:
        placement_x_m (float): Center location of the payload compartment from nose in meters.
        orientation (str): Optical alignment (e.g. Nadir Downward, Forward-Facing).
        compartment_length_m (float): Envelope length allocation.
        compartment_width_m (float): Envelope width allocation.
        compartment_height_m (float): Envelope height allocation.
        accessibility_description (str): access panel (e.g. Bottom hatch canopy).
    """

    placement_x_m: float
    orientation: str
    compartment_length_m: float
    compartment_width_m: float
    compartment_height_m: float
    accessibility_description: str
