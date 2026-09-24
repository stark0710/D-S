"""
WorkflowEngine Subsystem

Purpose:
    Defines the `WorkflowEngine` class, which serves as the public entry point for orchestrating workflow execution.

Role in Architecture:
    `WorkflowEngine` receives a `DesignContext`, resolves or accepts `WorkflowStage` steps, executes a `WorkflowPipeline`,
    validates execution order, tracks progress, stops on unrecoverable failures, and returns the updated `DesignContext`.
"""

from backend.design.common.context.design_context import DesignContext
from backend.design.studio.workflow.workflow_stage_result import WorkflowStageResult
from backend.design.studio.workflow.workflow_stage import WorkflowStage
from backend.design.studio.workflow.workflow_registry import WorkflowRegistry
from backend.design.studio.workflow.workflow_pipeline import WorkflowPipeline


class WorkflowEngine:
    """
    Public entry point service for aircraft design workflow execution.

    Design Principles:
        - Single Responsibility Principle: Workflow execution orchestration and progress tracking only.
        - Dependency Injection: Injects `WorkflowRegistry` and `WorkflowPipeline` collaborators.
    """

    def __init__(
        self,
        registry: WorkflowRegistry | None = None,
        pipeline: WorkflowPipeline | None = None
    ) -> None:
        """
        Initializes the WorkflowEngine.

        Args:
            registry (WorkflowRegistry | None): Injected workflow registry instance.
            pipeline (WorkflowPipeline | None): Injected workflow pipeline instance.
        """
        self._registry: WorkflowRegistry = registry if registry else WorkflowRegistry()
        self._pipeline: WorkflowPipeline = pipeline if pipeline else WorkflowPipeline()

    def run_workflow(
        self,
        context: DesignContext,
        stages: list[WorkflowStage] | None = None
    ) -> tuple[DesignContext, list[WorkflowStageResult]]:
        """
        Runs the specified workflow stages sequentially against the provided DesignContext.

        Args:
            context (DesignContext): Input design context.
            stages (list[WorkflowStage] | None): Optional list of workflow stage steps. If None, uses pipeline stages.

        Returns:
            tuple[DesignContext, list[WorkflowStageResult]]: Tuple of (updated DesignContext, aggregated stage results).
        """
        target_pipeline = self._pipeline
        if stages:
            target_pipeline = WorkflowPipeline(stages=stages)

        updated_ctx, results = target_pipeline.execute(context)
        updated_ctx.metadata.notes = f"Executed {len(results)} workflow stages."
        return updated_ctx, results
