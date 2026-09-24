"""
EngineeringParameter Domain Model

Purpose:
    Defines the `EngineeringParameter` domain model representing a single engineering parameter
    within the Torq Wings Design Studio backend.

Role in Architecture:
    `EngineeringParameter` is the canonical software representation of an engineering parameter
    (e.g., Payload Weight, Cruise Speed, Stall Speed, Flight Time, Battery Capacity).
    It extends `KnowledgeEntity` with parameter-specific metadata, classification, units, data types,
    and reference relationships while maintaining strict framework and infrastructure independence.
"""

from dataclasses import dataclass, field
from backend.models.knowledge_entity import KnowledgeEntity


@dataclass(slots=True)
class EngineeringParameter(KnowledgeEntity):
    """
    Canonical domain model for an Engineering Parameter in Torq Wings Design Studio.

    Inherits baseline identity attributes (`id`, `name`, `description`) from `KnowledgeEntity`
    and extends them with core parameter metadata required by the software domain.

    Attributes:
        id (str): Unique parameter identifier (inherited from KnowledgeEntity).
        name (str): Human-readable parameter name (inherited from KnowledgeEntity).
        description (str): Detailed parameter description (inherited from KnowledgeEntity).
        library (str): The parameter library this parameter belongs to (e.g., EPL-001_MISSION_PROFILE).
        parameter_group (str): Logical grouping within the library (e.g., Mission Requirements).
        engineering_classification (str): Engineering classification (e.g., Performance, Operational).
        unit (str | None): Physical unit of measure (e.g., kg, m/s, min), if applicable.
        data_type (str | None): Data type specification (e.g., Float, Integer, Enum, Boolean).
        default_value (str | None): Default initial value or baseline value represented as a string.
        allowed_values (list[str]): Permissible value options for discrete or enumerated parameters.
        reference_ids (list[str]): List of associated engineering reference or standard identifiers.
    """

    # Primary parameter classification & categorization
    library: str
    parameter_group: str
    engineering_classification: str

    # Value specifications and constraints
    unit: str | None = None
    data_type: str | None = None
    default_value: str | None = None
    allowed_values: list[str] = field(default_factory=list)
    reference_ids: list[str] = field(default_factory=list)
