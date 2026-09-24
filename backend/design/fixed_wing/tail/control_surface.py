"""
Fixed-Wing Tail Control Surface Geometry Subsystem

Purpose:
    Defines the `ControlSurfaces` class representing elevator and rudder dimensions and deflection bounds.

Role in Architecture:
    Stores control geometry including spans, chord ratios, areas, deflection limits,
    and hinge line placements.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ControlSurfaces:
    """
    Control surface sizing parameters for elevator and rudder.

    Attributes:
        elevator_span_m (float): Elevator span width in meters.
        elevator_chord_ratio (float): Chord ratio of elevator relative to horizontal tail chord (c_e / c_h).
        elevator_area_m2 (float): Elevator reference surface area in square meters.
        elevator_max_deflection_deg (float): Limit deflection angle in degrees (e.g. +/- 25 deg).
        elevator_hinge_location_pct (float): Location of the hinge line as a percentage of horizontal tail chord.
        
        rudder_height_m (float): Rudder vertical height in meters.
        rudder_chord_ratio (float): Chord ratio of rudder relative to vertical tail chord (c_r / c_v).
        rudder_area_m2 (float): Rudder reference surface area in square meters.
        rudder_max_deflection_deg (float): Limit deflection angle in degrees (e.g. +/- 30 deg).
        rudder_hinge_location_pct (float): Location of the hinge line as a percentage of vertical tail chord.
    """

    elevator_span_m: float
    elevator_chord_ratio: float
    elevator_area_m2: float
    elevator_max_deflection_deg: float
    elevator_hinge_location_pct: float
    
    rudder_height_m: float
    rudder_chord_ratio: float
    rudder_area_m2: float
    rudder_max_deflection_deg: float
    rudder_hinge_location_pct: float
