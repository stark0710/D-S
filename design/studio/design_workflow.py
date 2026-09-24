"""
DesignWorkflow Subsystem

Purpose:
    Defines the `DesignWorkflow` class responsible for orchestrating ordered workflow stage execution and error recovery.

Role in Architecture:
    `DesignWorkflow` manages sequential execution of registered design steps, tracks progress via `DesignStageManager`,
    collects artifacts, and handles workflow failure recovery.
"""

from typing import Callable, Any
from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.studio.design_artifact import DesignArtifact
from backend.design.studio.design_result import DesignResult
from backend.design.studio.design_stage_manager import DesignStageManager
from backend.design.studio.design_exception import WorkflowExecutionError


class DesignWorkflow:
    """
    Orchestration engine for executing ordered engineering workflow stages.

    Design Principles:
        - Template Method Pattern: Defines the skeletal workflow loop while delegating step execution to step handlers.
        - Single Responsibility Principle: Workflow loop orchestration and progress tracking.
    """

    def __init__(self, stage_manager: DesignStageManager | None = None) -> None:
        """
        Initializes the DesignWorkflow.

        Args:
            stage_manager (DesignStageManager | None): Injected stage manager instance.
        """
        self.stage_manager: DesignStageManager = (
            stage_manager if stage_manager else DesignStageManager()
        )
        self._steps: list[tuple[DesignStage, Callable[[DesignContext], tuple[DesignContext, list[DesignArtifact]]]]] = []

    def add_step(
        self,
        stage: DesignStage,
        handler: Callable[[DesignContext], tuple[DesignContext, list[DesignArtifact]]]
    ) -> None:
        """
        Registers a step handler for the specified workflow stage.

        Args:
            stage (DesignStage): Target workflow stage.
            handler (Callable): Step execution function receiving DesignContext and returning (updated_context, artifacts).
        """
        self._steps.append((stage, handler))

    def execute_workflow(self, context: DesignContext) -> DesignResult:
        """
        Executes all registered workflow steps sequentially against the provided DesignContext.

        Args:
            context (DesignContext): Input design context.

        Returns:
            DesignResult: Final workflow result summary.
        """
        all_artifacts: list[DesignArtifact] = []
        warnings: list[str] = []
        errors: list[str] = []
        current_ctx = context

        for stage, handler in self._steps:
            try:
                self.stage_manager.advance_stage(stage)
                current_ctx.update_stage(stage, DesignStatus.IN_PROGRESS)

                updated_ctx, artifacts = handler(current_ctx)
                current_ctx = updated_ctx

                all_artifacts.extend(artifacts)
                self.stage_manager.mark_completed(stage)
                current_ctx.update_stage(stage, DesignStatus.IN_PROGRESS, snapshot_summary=f"Completed workflow step '{stage.value}'.")

            except Exception as exc:
                self.stage_manager.mark_failed(stage)
                error_msg = f"Workflow stage '{stage.value}' failed: {str(exc)}"
                errors.append(error_msg)
                current_ctx.update_stage(stage, DesignStatus.FAILED)

                return DesignResult(
                    success=False,
                    final_design_context=current_ctx,
                    artifacts=all_artifacts,
                    warnings=warnings,
                    errors=errors,
                    metadata={"failed_stage": stage.value}
                )

        current_ctx.update_stage(DesignStage.COMPLETED, DesignStatus.COMPLETED, snapshot_summary="All workflow steps completed successfully.")

        return DesignResult(
            success=True,
            final_design_context=current_ctx,
            artifacts=all_artifacts,
            warnings=warnings,
            errors=errors,
            metadata={"completed_steps_count": len(self._steps)}
        )
