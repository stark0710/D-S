"""
Fixed-Wing Aircraft Configuration Result Subsystem

Purpose:
    Defines the `ConfigurationResult` class, which holds the output of the configuration selection framework.

Role in Architecture:
    `ConfigurationResult` is the data payload returned by the Configuration Engine.
    It carries the chosen configuration, alternative suggestions, rationales, recommendations, and warnings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(slots=True)
class ConfigurationResult:
    """
    Result of the Aircraft Configuration selection and evaluation process.

    Attributes:
        selected_configuration (Dict[str, str]): Selected layout attributes (wing position, propulsion, tail, gear, layout, etc.).
        configuration_score (float): Overall scoring index for the selected configuration.
        wing_configuration (str): Textual representation of selected wing position.
        propulsion_configuration (str): Textual representation of selected propulsion configuration.
        tail_configuration (str): Textual representation of selected tail configuration.
        landing_gear_configuration (str): Textual representation of selected landing gear.
        engineering_rationale (str): Detailed text justifying the selection based on aerodynamic and structural constraints.
        alternative_configurations (List[Dict[str, Any]]): Ranked list of alternative configurations and their scores.
        recommendations (List[str]): Design tips or suggestions for the chosen layout.
        warnings (List[str]): Operational warnings or configuration compromises.
        metadata (Dict[str, Any]): Generation metadata, timestamp, engine version, etc.
    """

    selected_configuration: Dict[str, str]
    configuration_score: float
    wing_configuration: str
    propulsion_configuration: str
    tail_configuration: str
    landing_gear_configuration: str
    engineering_rationale: str
    alternative_configurations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
