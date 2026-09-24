"""
Fixed-Wing Fuselage Internal Layout Subsystem

Purpose:
    Defines the `InternalLayout` class representing internal component positioning and cooling paths.

Role in Architecture:
    `InternalLayout` is a pure domain entity storing coordinate locations of internals
    relative to the nose (x-locations).
"""

from dataclasses import dataclass


@dataclass(slots=True)
class InternalLayout:
    """
    Longitudinal position coordinate layouts of systems inside the fuselage (relative to the nose).

    Attributes:
        payload_placement_x_m (float): Center location of the payload compartment from nose.
        battery_placement_x_m (float): Center location of the battery compartment from nose.
        flight_controller_placement_x_m (float): Location of the flight controller from nose.
        gps_placement_x_m (float): Location of the GPS receiver from nose.
        receiver_placement_x_m (float): Location of the RC receiver from nose.
        telemetry_placement_x_m (float): Location of the telemetry transmitter from nose.
        esc_placement_x_m (float): Location of the Electronic Speed Controller (ESC) from nose.
        
        power_distribution_location (str): Mounting zone for the power distribution board.
        cable_routing_path (str): Description of wire runs (e.g. Side floor channels).
        cooling_airflow_channel (str): Description of cooling duct intake and exhaust runs.
        service_access_description (str): Description of maintenance access panels.
    """

    payload_placement_x_m: float
    battery_placement_x_m: float
    flight_controller_placement_x_m: float
    gps_placement_x_m: float
    receiver_placement_x_m: float
    telemetry_placement_x_m: float
    esc_placement_x_m: float
    
    power_distribution_location: str
    cable_routing_path: str
    cooling_airflow_channel: str
    service_access_description: str
