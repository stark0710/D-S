"""
Pipeline Executor coordinating sequential stage executions.
"""
import time
from typing import List
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.pipeline.pipeline_stage import PipelineStage
from backend.design.fixed_wing.pipeline.pipeline_logger import PipelineLogger


class PipelineExecutor:
    def __init__(self, stages: List[PipelineStage], logger: PipelineLogger = None) -> None:
        self.stages = stages
        self.logger = logger or PipelineLogger()

    def execute(self, context: FixedWingPipelineContext) -> None:
        for stage in self.stages:
            stage_name = stage.__class__.__name__
            self.logger.log_stage_start(stage_name)
            t0 = time.time()
            try:
                stage.execute(context)
                duration = time.time() - t0
                self.logger.log_stage_success(stage_name, duration)
            except Exception as e:
                duration = time.time() - t0
                self.logger.log_stage_failure(stage_name, e, duration)
                raise e
