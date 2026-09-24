"""
ComponentSelectionPipeline Subsystem

Purpose:
    Defines the `ComponentSelectionPipeline` class responsible for orchestrating component retrieval and selection workflows.

Role in Architecture:
    `ComponentSelectionPipeline` acts as the execution pipeline for component selection.
    It receives a `ComponentSelectionRequest`, retrieves candidate records from `ComponentRepository`,
    delegates evaluation to `ComponentSelector`, and returns a `ComponentSelectionResult`.
"""

from backend.design.components.component_selection_request import ComponentSelectionRequest
from backend.design.components.component_selection_result import ComponentSelectionResult
from backend.design.components.component_repository import ComponentRepository
from backend.design.components.component_selector import ComponentSelector, DefaultComponentSelector


class ComponentSelectionPipeline:
    """
    Orchestration pipeline for hardware component selection.

    Design Principles:
        - Pipeline Pattern: Coordinates candidate retrieval and selector invocation.
        - Dependency Injection: Injects `ComponentRepository` and `ComponentSelector` collaborators.
    """

    def __init__(
        self,
        repository: ComponentRepository,
        selector: ComponentSelector | None = None
    ) -> None:
        """
        Initializes the ComponentSelectionPipeline.

        Args:
            repository (ComponentRepository): Injected component repository instance.
            selector (ComponentSelector | None): Injected selector instance. Defaults to DefaultComponentSelector if None.
        """
        self._repository: ComponentRepository = repository
        self._selector: ComponentSelector = selector if selector else DefaultComponentSelector()

    def execute(self, request: ComponentSelectionRequest) -> ComponentSelectionResult:
        """
        Executes component selection for the specified request.

        Args:
            request (ComponentSelectionRequest): Query request.

        Returns:
            ComponentSelectionResult: Final selected component result with candidate rankings.
        """
        raw_candidates = self._repository.get_components_by_category(
            category=request.category,
            filters=request.filters
        )

        return self._selector.select(request, raw_candidates)
