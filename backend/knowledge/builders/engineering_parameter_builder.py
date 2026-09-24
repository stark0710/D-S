"""
EngineeringParameterBuilder Subsystem

Purpose:
    Defines the `EngineeringParameterBuilder` class responsible for converting a `ParsedDocument`
    metadata dictionary into a strongly typed `EngineeringParameter` domain model.

Role in Architecture:
    `EngineeringParameterBuilder` implements the `EntityBuilder` interface within the Entity Construction Engine.
    It reads pre-extracted metadata from `document.metadata` and instantiates the canonical `EngineeringParameter`
    domain model, isolating entity construction from file reading, markdown parsing, and repository discovery.
"""

from typing import Any
from backend.knowledge.builders.entity_builder import EntityBuilder
from backend.models.parsed_document import ParsedDocument
from backend.models.engineering_parameter import EngineeringParameter


class MissingRequiredMetadataError(ValueError):
    """Raised when mandatory metadata fields (e.g., id or name) are missing."""
    pass


class EngineeringParameterBuilder(EntityBuilder):
    """
    Concrete EntityBuilder that constructs EngineeringParameter domain objects from ParsedDocument metadata.

    Responsibilities:
        - Extract mandatory metadata fields (`id`, `name`), with fallback to file_name conventions.
        - Map YAML metadata fields directly into `EngineeringParameter` attributes.
        - Utilize model defaults for missing optional metadata fields.

    Design Principles:
        - Single Responsibility Principle (SRP): Converts parsed document metadata to domain model only.
        - Framework Independence: Operates exclusively on pure dataclass domain models.

    Limitations:
        - Pure Constructor: Does not resolve foreign references (`reference_ids`) or perform range validation.
    """

    def build(self, document: ParsedDocument) -> EngineeringParameter:
        """
        Builds an EngineeringParameter domain instance from a ParsedDocument.

        Args:
            document (ParsedDocument): The parsed intermediate document containing metadata.

        Returns:
            EngineeringParameter: Strongly typed domain model object.

        Raises:
            MissingRequiredMetadataError: If required fields ('id', 'name') cannot be determined.
        """
        metadata: dict[str, Any] = document.metadata or {}
        file_name = document.repository_document.file_name if document.repository_document else ""

        # Extract id with fallback to filename prefix
        param_id = metadata.get("id")
        if not param_id and file_name:
            param_id = file_name.split("_")[0].removesuffix(".md").strip()

        if not param_id or not str(param_id).strip():
            raise MissingRequiredMetadataError(
                f"Missing required metadata field 'id' in document '{file_name}'."
            )

        # Extract name with fallback to filename
        param_name = metadata.get("name")
        if not param_name and file_name:
            param_name = file_name.removesuffix(".md").replace("_", " ").strip()

        if not param_name or not str(param_name).strip():
            raise MissingRequiredMetadataError(
                f"Missing required metadata field 'name' in document '{file_name}'."
            )

        # Extract optional fields with sensible defaults
        description = str(metadata.get("description", ""))
        library = str(metadata.get("library", ""))
        parameter_group = str(metadata.get("parameter_group", ""))
        engineering_classification = str(metadata.get("engineering_classification", ""))

        unit = metadata.get("unit")
        unit_str = str(unit) if unit is not None else None

        data_type = metadata.get("data_type")
        data_type_str = str(data_type) if data_type is not None else None

        default_value = metadata.get("default_value")
        default_value_str = str(default_value) if default_value is not None else None

        allowed_values_raw = metadata.get("allowed_values", [])
        allowed_values = [str(val) for val in allowed_values_raw] if isinstance(allowed_values_raw, list) else []

        reference_ids_raw = metadata.get("reference_ids", [])
        reference_ids = [str(ref) for ref in reference_ids_raw] if isinstance(reference_ids_raw, list) else []

        return EngineeringParameter(
            id=str(param_id).strip(),
            name=str(param_name).strip(),
            description=description,
            library=library,
            parameter_group=parameter_group,
            engineering_classification=engineering_classification,
            unit=unit_str,
            data_type=data_type_str,
            default_value=default_value_str,
            allowed_values=allowed_values,
            reference_ids=reference_ids,
        )
