"""
StageValidator Subsystem

Purpose:
    Defines the `StageValidator` class responsible for validating stage dependencies, sequence ordering, and detecting circular dependencies.

Role in Architecture:
    `StageValidator` ensures that a sequence of `DesignStage` steps satisfies all pre-requisite dependency constraints
    and contains no circular dependency cycles prior to execution.
"""

from backend.design.studio.stages.design_stage import DesignStage


class StageValidationError(ValueError):
    """Raised when stage sequence dependency or ordering validation fails."""
    pass


class StageValidator:
    """
    Validator for design stage sequences and dependencies.

    Design Principles:
        - Single Responsibility Principle: Sequence dependency validation and cycle detection only.
    """

    def validate_stage_sequence(self, stages: list[DesignStage]) -> bool:
        """
        Validates stage dependencies, ordering, and circular dependency safety for a sequence of stages.

        Args:
            stages (list[DesignStage]): List of stages in planned execution order.

        Returns:
            bool: True if sequence is valid.

        Raises:
            StageValidationError: If ordering violates required dependencies or contains circular cycles.
        """
        stage_names_in_order: list[str] = [s.stage_name for s in stages]
        stage_map: dict[str, DesignStage] = {s.stage_name: s for s in stages}

        # 1. Dependency Ordering check
        for idx, stage in enumerate(stages):
            for dep in stage.required_dependencies:
                if dep not in stage_names_in_order:
                    raise StageValidationError(
                        f"Stage '{stage.stage_name}' requires dependency '{dep}' which is missing from the workflow sequence."
                    )
                dep_idx = stage_names_in_order.index(dep)
                if dep_idx >= idx:
                    raise StageValidationError(
                        f"Stage '{stage.stage_name}' requires dependency '{dep}' to execute prior (Found '{dep}' at index {dep_idx}, current at {idx})."
                    )

        # 2. Circular Dependency check
        self._detect_circular_dependencies(stage_map)
        return True

    def _detect_circular_dependencies(self, stage_map: dict[str, DesignStage]) -> None:
        """Performs Depth First Search (DFS) to detect circular dependency cycles."""
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)

            stage = stage_map.get(node)
            if stage:
                for dep in stage.required_dependencies:
                    if dep not in visited:
                        if dep in stage_map:
                            dfs(dep)
                    elif dep in rec_stack:
                        raise StageValidationError(
                            f"Circular dependency cycle detected involving stage '{node}' and dependency '{dep}'."
                        )

            rec_stack.remove(node)

        for name in stage_map:
            if name not in visited:
                dfs(name)
