"""
BuilderRegistry Subsystem

Purpose:
    Defines the `BuilderRegistry` class responsible for registering, maintaining, and retrieving
    concrete `EntityBuilder` instances mapped by document classification type strings.

Role in Architecture:
    `BuilderRegistry` serves as the central builder lookup and discovery engine within the Entity Construction Engine.
    By replacing hardcoded `if/elif` conditionals with dynamic registry lookups, it enforces the
    Open/Closed Principle (OCP) and enables seamless registration of future entity builders
    (e.g., MissionDomainBuilder, MissionCategoryBuilder, MaterialBuilder).
"""

from backend.knowledge.builders.entity_builder import EntityBuilder


class BuilderRegistryError(ValueError):
    """Base exception class for BuilderRegistry operations."""
    pass


class DuplicateBuilderRegistrationError(BuilderRegistryError):
    """Raised when attempting to register a builder for an already registered document type."""
    pass


class UnregisteredBuilderError(BuilderRegistryError, KeyError):
    """Raised when looking up an EntityBuilder for a document type that has not been registered."""
    pass


class BuilderRegistry:
    """
    Registry container for managing EntityBuilder instances by document type string.

    Responsibilities:
        - Register concrete `EntityBuilder` implementations against document classification strings.
        - Prevent duplicate builder registrations for the same document type.
        - Look up and return the appropriate `EntityBuilder` for a given document type.
        - Query registration state and list all currently registered document types.

    Design Principles:
        - Open/Closed Principle (OCP): Unlimited new entity builders can be registered dynamically.
        - Single Responsibility Principle (SRP): Manages builder mappings only.
    """

    def __init__(self) -> None:
        """Initializes an empty BuilderRegistry mapping."""
        self._builders: dict[str, EntityBuilder] = {}

    def register(self, document_type: str, builder: EntityBuilder) -> None:
        """
        Registers an EntityBuilder instance for a specified document classification type.

        Args:
            document_type (str): Classification string (e.g., 'engineering_parameter').
            builder (EntityBuilder): Concrete EntityBuilder instance to handle this document type.

        Raises:
            ValueError: If document_type is empty or builder is invalid.
            DuplicateBuilderRegistrationError: If a builder is already registered for document_type.
        """
        if not document_type or not document_type.strip():
            raise ValueError("Cannot register builder with an empty or whitespace document_type.")

        if not isinstance(builder, EntityBuilder):
            raise ValueError(f"Expected builder of type EntityBuilder, got '{type(builder).__name__}'.")

        normalized_type = document_type.strip().lower()

        if normalized_type in self._builders:
            raise DuplicateBuilderRegistrationError(
                f"Builder registration failed: A builder is already registered for document type '{normalized_type}'."
            )

        self._builders[normalized_type] = builder

    def get_builder(self, document_type: str) -> EntityBuilder:
        """
        Retrieves the registered EntityBuilder for a document type.

        Args:
            document_type (str): Classification string to look up.

        Returns:
            EntityBuilder: The registered builder instance.

        Raises:
            UnregisteredBuilderError: If no builder has been registered for document_type.
        """
        normalized_type = (document_type or "").strip().lower()

        if normalized_type not in self._builders:
            raise UnregisteredBuilderError(
                f"No builder registered for document type: '{document_type}'."
            )

        return self._builders[normalized_type]

    def has_builder(self, document_type: str) -> bool:
        """
        Checks whether an EntityBuilder is registered for a document type.

        Args:
            document_type (str): Classification string to check.

        Returns:
            bool: True if a builder is registered; False otherwise.
        """
        normalized_type = (document_type or "").strip().lower()
        return normalized_type in self._builders

    def registered_types(self) -> list[str]:
        """
        Returns a sorted list of all currently registered document classification types.

        Returns:
            list[str]: Sorted list of registered document type strings.
        """
        return sorted(self._builders.keys())
