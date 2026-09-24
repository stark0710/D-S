"""
ComponentSelector Subsystem

Purpose:
    Defines the abstract `ComponentSelector` interface and concrete `DefaultComponentSelector` implementation.

Role in Architecture:
    `ComponentSelector` evaluates raw candidate components retrieved from `ComponentRepository` against a `ComponentSelectionRequest`,
    scores match suitability and compatibility, ranks options, and constructs a `ComponentSelectionResult`.
"""

from abc import ABC, abstractmethod
from typing import Any
from backend.design.components.component_selection_request import ComponentSelectionRequest
from backend.design.components.component_candidate import ComponentCandidate
from backend.design.components.component_selection_result import ComponentSelectionResult


class ComponentSelector(ABC):
    """
    Abstract interface for evaluating and selecting component candidates.
    """

    @abstractmethod
    def select(
        self,
        request: ComponentSelectionRequest,
        raw_candidates: list[dict[str, Any]]
    ) -> ComponentSelectionResult:
        """
        Evaluates candidate components against request criteria.

        Args:
            request (ComponentSelectionRequest): Query request.
            raw_candidates (list[dict[str, Any]]): Raw candidate component attribute dictionaries.

        Returns:
            ComponentSelectionResult: Evaluated and ranked selection result.
        """
        pass


class DefaultComponentSelector(ComponentSelector):
    """
    Default component selector scoring requirements and constraints.

    Design Principles:
        - Single Responsibility Principle: Candidate scoring and ranking only.
        - Aircraft Independent: Operates strictly on component numerical properties and requirement criteria.
    """

    def select(
        self,
        request: ComponentSelectionRequest,
        raw_candidates: list[dict[str, Any]]
    ) -> ComponentSelectionResult:
        candidates: list[ComponentCandidate] = []

        for item in raw_candidates:
            score, compat_score, notes = self._evaluate_candidate(request, item)
            candidate = ComponentCandidate(
                component=item,
                score=round(score, 2),
                compatibility_score=round(compat_score, 2),
                selection_notes=notes,
                metadata={"category": request.category.value}
            )
            candidates.append(candidate)

        # Sort candidates by overall score descending
        candidates.sort(key=lambda c: (c.score, c.compatibility_score), reverse=True)

        selected = candidates[0] if candidates else None

        if selected:
            name = selected.component.get("name") or selected.component.get("id") or "Component"
            summary = (
                f"Selected {selected.component.get('category', request.category.value)}: '{name}' "
                f"with score {selected.score} (Evaluated {len(candidates)} options)."
            )
        else:
            summary = f"No suitable {request.category.value} candidate found matching request criteria."

        return ComponentSelectionResult(
            selected_component=selected,
            candidates=candidates,
            selection_summary=summary,
            metadata={"evaluated_count": len(raw_candidates)}
        )

    def _evaluate_candidate(
        self,
        request: ComponentSelectionRequest,
        item: dict[str, Any]
    ) -> tuple[float, float, list[str]]:
        """Evaluates score, compatibility, and diagnostic notes for a single item."""
        score = 1.0
        compat_score = 1.0
        notes: list[str] = []

        # Constraint check: max_weight_g
        max_weight = request.constraints.get("max_weight_g")
        if max_weight is not None and "weight_g" in item:
            item_weight = float(item["weight_g"])
            if item_weight > max_weight:
                score -= 0.30
                compat_score -= 0.40
                notes.append(f"Exceeds max weight constraint ({item_weight}g > {max_weight}g).")

        # Requirement check: target numeric metrics
        for req_key, req_val in request.requirements.items():
            if req_key in item and isinstance(req_val, (int, float)):
                item_val = float(item[req_key])
                req_num = float(req_val)
                if req_num > 0:
                    diff_ratio = abs(item_val - req_num) / req_num
                    if diff_ratio > 0.5:
                        score -= 0.20
                        notes.append(f"Significant variance in {req_key} (Target: {req_num}, Actual: {item_val}).")

        score = max(0.0, min(1.0, score))
        compat_score = max(0.0, min(1.0, compat_score))

        if not notes:
            notes.append("Candidate matches all specified constraints and requirements.")

        return score, compat_score, notes
