"""
DesignStage Enumeration Subsystem

Purpose:
    Defines the `DesignStage` enumeration representing lifecycle stages of the aircraft design workflow.

Role in Architecture:
    `DesignStage` tracks the progression of a `DesignContext` through requirement collection, validation,
    mission analysis, vehicle recommendation, studio sizing, optimization, and reporting.
"""

from enum import Enum


class DesignStage(str, Enum):
    """
    Aircraft design workflow stage classification.

    Members:
        REQUIREMENT_COLLECTION: Initial acquisition of user requirement parameters.
        REQUIREMENT_VALIDATION: Execution of requirement validation pipeline.
        MISSION_ANALYSIS: Physics analysis of hover/cruise power, energy budget, and payload fraction.
        VEHICLE_RECOMMENDATION: MCDA suitability scoring and recommendation report generation.
        VEHICLE_SELECTION: User category selection approval (Engineering Advisor mode) or explicit selection (Manual mode).
        DESIGN_ROUTING: Dispatch of validated requirements and specs to chosen design studio.
        DRONE_DESIGN: Multirotor drone propulsion, frame, hover, and component sizing.
        FIXED_WING_DESIGN: Fixed-wing UAV wing loading, drag polar, and tail sizing.
        VTOL_DESIGN: Hybrid VTOL dual propulsion and transition energy sizing.
        OPTIMIZATION: Multi-objective Pareto trade-off optimization execution.
        REPORTING: Generation of final design summary reports (PDF, Markdown, JSON).
        COMPLETED: Design process finished successfully.
    """
    REQUIREMENT_COLLECTION = "REQUIREMENT_COLLECTION"
    REQUIREMENT_VALIDATION = "REQUIREMENT_VALIDATION"
    MISSION_ANALYSIS = "MISSION_ANALYSIS"
    VEHICLE_RECOMMENDATION = "VEHICLE_RECOMMENDATION"
    VEHICLE_SELECTION = "VEHICLE_SELECTION"
    DESIGN_ROUTING = "DESIGN_ROUTING"
    DRONE_DESIGN = "DRONE_DESIGN"
    FIXED_WING_DESIGN = "FIXED_WING_DESIGN"
    VTOL_DESIGN = "VTOL_DESIGN"
    OPTIMIZATION = "OPTIMIZATION"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"
