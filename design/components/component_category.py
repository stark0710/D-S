"""
ComponentCategory Enumeration Subsystem

Purpose:
    Defines the `ComponentCategory` enumeration representing hardware component classifications.

Role in Architecture:
    `ComponentCategory` classifies components in the component database and selection requests across all design studios.
"""

from enum import Enum


class ComponentCategory(str, Enum):
    """
    Aircraft hardware component classification.

    Members:
        MOTOR: Brushless or brushed propulsion motor.
        ESC: Electronic Speed Controller.
        BATTERY: Energy storage battery pack (LiPo, Li-ion, LiFePO4).
        PROPELLER: Airfoil rotor or propeller.
        FRAME: Airframe structure or chassis.
        FLIGHT_CONTROLLER: Main autopilot / flight control unit.
        SERVO: Actuator servo motor for control surfaces or tilt mechanisms.
        GPS: Satellite navigation module.
        TELEMETRY: Radio telemetry transceiver.
        RECEIVER: RC control receiver.
        CAMERA: Optical imaging or FPV camera payload.
        PAYLOAD: Mission-specific payload sensor or cargo container.
        POWER_DISTRIBUTION_BOARD: Power distribution board (PDB).
        BEC: Battery Eliminator Circuit voltage regulator.
        SENSOR: Environmental or flight sensor (airspeed, LIDAR, sonar).
        LANDING_GEAR: Structural landing gear or skids.
        CUSTOM: User-defined custom hardware component.
    """
    MOTOR = "MOTOR"
    ESC = "ESC"
    BATTERY = "BATTERY"
    PROPELLER = "PROPELLER"
    FRAME = "FRAME"
    FLIGHT_CONTROLLER = "FLIGHT_CONTROLLER"
    SERVO = "SERVO"
    GPS = "GPS"
    TELEMETRY = "TELEMETRY"
    RECEIVER = "RECEIVER"
    CAMERA = "CAMERA"
    PAYLOAD = "PAYLOAD"
    POWER_DISTRIBUTION_BOARD = "POWER_DISTRIBUTION_BOARD"
    BEC = "BEC"
    SENSOR = "SENSOR"
    LANDING_GEAR = "LANDING_GEAR"
    CUSTOM = "CUSTOM"
