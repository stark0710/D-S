"""
Fixed-Wing Wing Geometry Subsystem

Purpose:
    Defines the `WingGeometry` domain model holding sized physical dimensional properties of the wing.

Role in Architecture:
    `WingGeometry` is a pure domain entity that stores the complete set of sized wing dimensions
    determined by the Wing Engineering Framework.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class WingGeometry:
    """
    Sized geometry parameters for the primary lifting wing surface.

    Attributes:
        span_m (float): Full wingspan tip-to-tip in meters (b).
        area_m2 (float): Reference planform wing area in square meters (S).
        aspect_ratio (float): Aspect ratio of the wing (b^2 / S).
        wing_loading_kg_m2 (float): Wing loading parameter (MTOW / S) in kg/m2.
        root_chord_m (float): Wing root chord length in meters.
        tip_chord_m (float): Wing tip chord length in meters.
        taper_ratio (float): Ratio of tip chord to root chord (tip_chord / root_chord).
        sweep_angle_deg (float): Leading edge sweep angle in degrees.
        dihedral_angle_deg (float): Wing dihedral angle in degrees.
        wing_incidence_deg (float): Wing mounting incidence angle on fuselage in degrees.
        mean_aerodynamic_chord_m (float): Mean Aerodynamic Chord (MAC) length in meters.
        quarter_chord_x_m (float): Longitudinal distance from the root leading edge to the quarter-chord point of the MAC.
        reference_area_m2 (float): Reference wing area in square meters (typically equals S).
    """

    span_m: float
    area_m2: float
    aspect_ratio: float
    wing_loading_kg_m2: float
    root_chord_m: float
    tip_chord_m: float
    taper_ratio: float
    sweep_angle_deg: float
    dihedral_angle_deg: float
    wing_incidence_deg: float
    mean_aerodynamic_chord_m: float
    quarter_chord_x_m: float
    reference_area_m2: float
