"""
Fixed-Wing Fuselage Mounting Interfaces Subsystem

Purpose:
    Defines the `MountingInterfaces` class representing physical fasteners, firewalls, and hatches.

Role in Architecture:
    `MountingInterfaces` stores structural connection locations, main gear positions,
    bolt hardware types, and access panels for manufacture.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class MountingInterfaces:
    """
    Structural attachment hardware specifications and mounting dimensions.

    Attributes:
        wing_mounting_style (str): Physical wing connection (e.g. Saddle mount, Through-tube).
        wing_mounting_hardware (str): Bolts and hardware size (e.g. 4x M4 steel bolts).
        tail_mounting_style (str): Physical stabilizer mounting (e.g. Clamp to boom, Tail cone bulkheads).
        propulsion_mount_type (str): Engine firewall style (e.g. 50x50mm wood/carbon firewall).
        landing_gear_mount_type (str): Landing gear attachment style.
        main_gear_attachment_x_m (float): Longitudinal location of main landing gear attachment from nose.
        nose_gear_attachment_x_m (float): Longitudinal location of nose landing gear attachment from nose.
        access_panels_description (str): access hatches (e.g. Top battery hatch, bottom payload panel).
    """

    wing_mounting_style: str
    wing_mounting_hardware: str
    tail_mounting_style: str
    propulsion_mount_type: str
    landing_gear_mount_type: str
    main_gear_attachment_x_m: float
    nose_gear_attachment_x_m: float
    access_panels_description: str
