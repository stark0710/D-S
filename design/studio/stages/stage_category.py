"""
StageCategory Enumeration Subsystem

Purpose:
    Defines the `StageCategory` enumeration representing reusable design stage classifications.

Role in Architecture:
    `StageCategory` classifies workflow stage steps across all Torq Wings Aircraft Design Studios.
"""

from enum import Enum


class StageCategory(str, Enum):
    """
    Reusable design workflow stage classification.

    Members:
        VALIDATION: Requirement model validation.
        MISSION_ANALYSIS: Mission physics & constraint profile analysis.
        CONFIGURATION: Aircraft structural/layout configuration setup.
        COMPONENT_SELECTION: Component database selection.
        COMPATIBILITY: Inter-component compatibility verification.
        CONSTRAINT_EVALUATION: Engineering design constraint verification.
        PERFORMANCE_EVALUATION: Physics performance analysis (aerodynamics, power, endurance).
        ENGINEERING_SCORING: Quantitative multi-criteria engineering scoring.
        RANKING: Candidate design ranking.
        OPTIMIZATION: Multi-objective trade-off optimization loop.
        ARTIFACT_GENERATION: CAD/geometry artifact generation.
        REPORT_GENERATION: Detailed PDF/Markdown engineering report compilation.
        PERSISTENCE: Design state database persistence.
        COMPLETION: Final workflow completion.
    """
    VALIDATION = "VALIDATION"
    MISSION_ANALYSIS = "MISSION_ANALYSIS"
    CONFIGURATION = "CONFIGURATION"
    COMPONENT_SELECTION = "COMPONENT_SELECTION"
    COMPATIBILITY = "COMPATIBILITY"
    CONSTRAINT_EVALUATION = "CONSTRAINT_EVALUATION"
    PERFORMANCE_EVALUATION = "PERFORMANCE_EVALUATION"
    ENGINEERING_SCORING = "ENGINEERING_SCORING"
    RANKING = "RANKING"
    OPTIMIZATION = "OPTIMIZATION"
    ARTIFACT_GENERATION = "ARTIFACT_GENERATION"
    REPORT_GENERATION = "REPORT_GENERATION"
    PERSISTENCE = "PERSISTENCE"
    COMPLETION = "COMPLETION"
