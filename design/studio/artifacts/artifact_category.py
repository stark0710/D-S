"""
ArtifactCategory Enumeration Subsystem

Purpose:
    Defines the `ArtifactCategory` enumeration representing standardized engineering artifact classifications.

Role in Architecture:
    `ArtifactCategory` classifies engineering outputs produced by Torq Wings Aircraft Design Studios.
"""

from enum import Enum


class ArtifactCategory(str, Enum):
    """
    Standardized engineering artifact classifications.

    Members:
        MISSION: Mission profile definition & specs.
        REQUIREMENTS: Aircraft operational/payload requirement models.
        AIRCRAFT_CONFIGURATION: Overall layout & structural configuration.
        WING_DESIGN: Wing planform, airfoil, and geometry spec.
        FUSELAGE_DESIGN: Fuselage geometry & volumetric layout spec.
        TAIL_DESIGN: Empennage / tail surface geometry spec.
        MOTOR_SELECTION: Motor selection specifications.
        ESC_SELECTION: Electronic Speed Controller (ESC) selection.
        BATTERY_SELECTION: Battery pack capacity & C-rating selection.
        PROPELLER_SELECTION: Propeller diameter & pitch selection.
        SERVO_SELECTION: Actuator & servo selection.
        FLIGHT_CONTROLLER_SELECTION: Avionics & FC hardware selection.
        ELECTRONICS_LAYOUT: Wiring, power distribution, and schematic layout.
        CG_ANALYSIS: Center of Gravity (CG) location and margin calculation.
        WEIGHT_BREAKDOWN: Detailed mass properties and weight budget breakdown.
        PERFORMANCE_ANALYSIS: Endurance, range, climb rate, airspeed analysis.
        AERODYNAMIC_ANALYSIS: Lift, drag, L/D ratio, polar curve analysis.
        POWER_SYSTEM: Electrical power draw, thermal, and current budget.
        OPTIMIZATION: Trade-off optimization history and Pareto front analysis.
        CAD_MODEL: 3D CAD model file or geometry parameters.
        ENGINEERING_DRAWING: 2D dimensioned engineering drawing specification.
        SIMULATION: Flight dynamics / CFD / FEA simulation output dataset.
        ENGINEERING_REPORT: Compiled PDF/Markdown engineering summary report.
        VALIDATION: Requirement & constraint validation log record.
        CUSTOM: User-defined custom engineering artifact.
    """
    MISSION = "MISSION"
    REQUIREMENTS = "REQUIREMENTS"
    AIRCRAFT_CONFIGURATION = "AIRCRAFT_CONFIGURATION"
    WING_DESIGN = "WING_DESIGN"
    FUSELAGE_DESIGN = "FUSELAGE_DESIGN"
    TAIL_DESIGN = "TAIL_DESIGN"
    MOTOR_SELECTION = "MOTOR_SELECTION"
    ESC_SELECTION = "ESC_SELECTION"
    BATTERY_SELECTION = "BATTERY_SELECTION"
    PROPELLER_SELECTION = "PROPELLER_SELECTION"
    SERVO_SELECTION = "SERVO_SELECTION"
    FLIGHT_CONTROLLER_SELECTION = "FLIGHT_CONTROLLER_SELECTION"
    ELECTRONICS_LAYOUT = "ELECTRONICS_LAYOUT"
    CG_ANALYSIS = "CG_ANALYSIS"
    WEIGHT_BREAKDOWN = "WEIGHT_BREAKDOWN"
    PERFORMANCE_ANALYSIS = "PERFORMANCE_ANALYSIS"
    AERODYNAMIC_ANALYSIS = "AERODYNAMIC_ANALYSIS"
    POWER_SYSTEM = "POWER_SYSTEM"
    OPTIMIZATION = "OPTIMIZATION"
    CAD_MODEL = "CAD_MODEL"
    ENGINEERING_DRAWING = "ENGINEERING_DRAWING"
    SIMULATION = "SIMULATION"
    ENGINEERING_REPORT = "ENGINEERING_REPORT"
    VALIDATION = "VALIDATION"
    CUSTOM = "CUSTOM"
