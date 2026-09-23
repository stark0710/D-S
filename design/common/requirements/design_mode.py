"""
DesignMode Enumeration Subsystem

Purpose:
    Defines the `DesignMode` enumeration representing supported design workflow modes.

Role in Architecture:
    `DesignMode` specifies whether the design process executes in `ENGINEERING_ADVISOR` mode (AI recommends category with explanations)
    or `MANUAL` mode (user explicitly selects category bypassing recommendations).
"""

from enum import Enum


class DesignMode(str, Enum):
    """
    Design workflow execution mode.

    Members:
        ENGINEERING_ADVISOR: AI analyzes requirements, recommends categories with explainable trade-offs, user approves before studio launch.
        MANUAL: User specifies aircraft category directly, bypassing vehicle recommendation.
    """
    ENGINEERING_ADVISOR = "ENGINEERING_ADVISOR"
    MANUAL = "MANUAL"
