"""
Fixed-Wing Fuselage Geometry Subsystem

Purpose:
    Defines the `FuselageGeometry` class holding primary sized fuselage parameters.

Role in Architecture:
    `FuselageGeometry` is a pure domain entity storing overall length, width, height, nose,
    tail cone, and specific compartment locations.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class FuselageGeometry:
    """
    Sized geometry parameters and compartment dimensions of the fuselage body.

    Attributes:
        length_m (float): Total fuselage length in meters.
        width_m (float): Maximum fuselage width in meters.
        height_m (float): Maximum fuselage height in meters.
        nose_length_m (float): Nose cone section length in meters.
        tail_cone_length_m (float): Tail cone section length in meters.
        cross_section_type (str): Shape profile (e.g. Rectangular, Circular, Elliptical).
        wing_attachment_x_m (float): Wing mounting interface location in meters from nose.
        tail_attachment_x_m (float): Tail mounting interface location in meters from nose.
        
        payload_bay_length_m (float): Sized length of the payload bay in meters.
        payload_bay_width_m (float): Sized width of the payload bay in meters.
        payload_bay_height_m (float): Sized height of the payload bay in meters.
        payload_bay_volume_m3 (float): Total volume of the payload bay compartment in cubic meters.
        
        battery_bay_length_m (float): Sized length of the battery bay in meters.
        battery_bay_width_m (float): Sized width of the battery bay in meters.
        battery_bay_height_m (float): Sized height of the battery bay in meters.
        battery_bay_volume_m3 (float): Total volume of the battery bay compartment in cubic meters.
        
        avionics_bay_length_m (float): Sized length of the avionics bay in meters.
        avionics_bay_width_m (float): Sized width of the avionics bay in meters.
        avionics_bay_height_m (float): Sized height of the avionics bay in meters.
        
        total_volume_m3 (float): Sized volume of the entire fuselage in cubic meters.
    """

    length_m: float
    width_m: float
    height_m: float
    nose_length_m: float
    tail_cone_length_m: float
    cross_section_type: str
    wing_attachment_x_m: float
    tail_attachment_x_m: float
    
    payload_bay_length_m: float
    payload_bay_width_m: float
    payload_bay_height_m: float
    payload_bay_volume_m3: float
    
    battery_bay_length_m: float
    battery_bay_width_m: float
    battery_bay_height_m: float
    battery_bay_volume_m3: float
    
    avionics_bay_length_m: float
    avionics_bay_width_m: float
    avionics_bay_height_m: float
    
    total_volume_m3: float
