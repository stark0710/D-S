"""
WorkflowPipeline Subsystem

Purpose:
    Defines the `WorkflowPipeline` class responsible for orchestrating sequential `WorkflowStage` executions via `WorkflowExecutor`.

Role in Architecture:
    `WorkflowPipeline` manages ordered stage execution, invokes `WorkflowExecutor`, aggregates `WorkflowStageResult` objects,
    and returns updated `DesignContext` state.
"""

from backend.design.common.context.design_context import DesignContext
from backend.design.studio.workflow.workflow_stage_result import WorkflowStageResult
from backend.design.studio.workflow.workflow_stage import WorkflowStage
from backend.design.studio.workflow.workflow_executor import WorkflowExecutor


class WorkflowPipeline:
    """
    Pipeline for executing sequential workflow stage steps.

    Design Principles:
        - Pipeline Pattern: Sequential execution of workflow stage steps.
        - Dependency Injection: Injects `WorkflowExecutor` collaborator.
    """

    def __init__(
        self,
        stages: list[WorkflowStage] | None = None,
        executor: WorkflowExecutor | None = None
    ) -> None:
        """
        Initializes the WorkflowPipeline.

        Args:
            stages (list[WorkflowStage] | None): Optional initial list of workflow stages.
            executor (WorkflowExecutor | None): Injected workflow executor instance.
        """
        self._stages: list[WorkflowStage] = list(stages) if stages else []
        self._executor: WorkflowExecutor = executor if executor else WorkflowExecutor()

    def add_stage(self, stage: WorkflowStage) -> None:
        """Appends a new workflow stage to the pipeline sequence."""
        self._stages.append(stage)

    def execute(self, context: DesignContext) -> tuple[DesignContext, list[WorkflowStageResult]]:
        """
        Executes all registered stages in sequence.

        Args:
            context (DesignContext): Input design context.

        Returns:
            tuple[DesignContext, list[WorkflowStageResult]]: Tuple of (final DesignContext, aggregated stage results).
        """
        current_ctx = context
        stage_results: list[WorkflowStageResult] = []

        for stage in self._stages:
            current_ctx, res = self._executor.execute_stage(stage, current_ctx)
            stage_results.append(res)

            if not res.success:
                break  # Stop pipeline execution on stage failure

        return current_ctx, stage_results
