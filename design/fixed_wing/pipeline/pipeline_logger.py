"""
Pipeline Logger facade for Fixed-Wing Aircraft Design Pipeline.
"""
import logging


class PipelineLogger:
    def __init__(self, name: str = "FixedWingDesignPipeline") -> None:
        self.logger = logging.getLogger(name)

    def log_stage_start(self, stage_name: str) -> None:
        self.logger.info(f"Starting pipeline stage: {stage_name}")

    def log_stage_success(self, stage_name: str, duration: float) -> None:
        self.logger.info(f"Successfully completed stage: {stage_name} in {duration:.4f}s")

    def log_stage_failure(self, stage_name: str, error: Exception, duration: float) -> None:
        self.logger.error(f"Failed pipeline stage: {stage_name} with error: {error} after {duration:.4f}s")

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)
