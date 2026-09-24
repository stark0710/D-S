"""
WorkflowExecutor Subsystem

Purpose:
    Defines the `WorkflowExecutor` class responsible for executing a single `WorkflowStage` with exception handling, retries, and timing metrics.

Role in Architecture:
    `WorkflowExecutor` executes individual stage steps, captures timing metrics, handles retryable exceptions, and produces a `WorkflowStageResult`.
"""

import time
from datetime import datetime, timezone
from backend.design.common.context.design_context import DesignContext
from backend.design.studio.workflow.workflow_stage_result import WorkflowStageResult
from backend.design.studio.workflow.workflow_stage import WorkflowStage
from backend.design.studio.workflow.workflow_exception import RetryableWorkflowError, StageExecutionError


class WorkflowExecutor:
    """
    Executor for individual workflow stages.

    Design Principles:
        - Single Responsibility Principle: Single stage execution, retry handling, and metrics capture only.
    """

    def execute_stage(
        self,
        stage: WorkflowStage,
        context: DesignContext,
        max_retries: int = 0
    ) -> tuple[DesignContext, WorkflowStageResult]:
        """
        Executes a single WorkflowStage with timing metrics and retry handling.

        Args:
            stage (WorkflowStage): Target workflow stage step.
            context (DesignContext): Input design context.
            max_retries (int): Maximum retry attempts for RetryableWorkflowError.

        Returns:
            tuple[DesignContext, WorkflowStageResult]: Tuple of (updated DesignContext, stage result summary).
        """
        retries = 0
        while True:
            started_at = datetime.now(timezone.utc).isoformat()
            t0 = time.time()

            try:
                updated_ctx, res = stage.execute(context)
                t1 = time.time()
                res.duration = round(t1 - t0, 4)
                return updated_ctx, res

            except RetryableWorkflowError as r_err:
                retries += 1
                if retries <= max_retries:
                    continue  # Retry execution
                t1 = time.time()
                res_fail = WorkflowStageResult(
                    stage_name=stage.stage_name,
                    success=False,
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    duration=round(t1 - t0, 4),
                    errors=[f"Stage '{stage.stage_name}' failed after {retries} retries: {str(r_err)}"]
                )
                raise StageExecutionError(res_fail.errors[0]) from r_err

            except Exception as exc:
                t1 = time.time()
                res_fail = WorkflowStageResult(
                    stage_name=stage.stage_name,
                    success=False,
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    duration=round(t1 - t0, 4),
                    errors=[f"Stage '{stage.stage_name}' failed: {str(exc)}"]
                )
                raise StageExecutionError(res_fail.errors[0]) from exc
