"""
Fixed-Wing/Multirotor/VTOL Shared Optimization Logger

Logs parameter selections, metrics, status events, and summary specifications.
"""

import logging
from typing import List
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_result import OptimizationResult

class OptimizationLogger:
    """
    Standard logger wrapper tracking design synthesis evaluations.
    """
    def __init__(self, name: str = "OptimizationLogger") -> None:
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
        self.logs: List[str] = []

    def info(self, msg: str) -> None:
        self.logger.info(msg)
        self.logs.append(f"INFO: {msg}")

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)
        self.logs.append(f"WARN: {msg}")

    def error(self, msg: str) -> None:
        self.logger.error(msg)
        self.logs.append(f"ERROR: {msg}")

    def log_candidate(self, candidate: OptimizationCandidate) -> None:
        vars_str = ", ".join(f"{k}={v}" for k, v in candidate.design_variables.items())
        if candidate.constraints_passed:
            self.info(f"Candidate [{vars_str}] passed constraints. Score: {candidate.overall_score:.4f}")
        else:
            reasons = "; ".join(f"{k}: {v['reason']}" for k, v in candidate.constraint_results.items() if v['status'] == 'FAIL')
            self.info(f"Candidate [{vars_str}] rejected. Failures: {reasons}")

    def log_summary(self, result: OptimizationResult) -> None:
        self.info(f"Optimization completed in {result.execution_time_seconds:.4f} seconds.")
        self.info(f"Evaluated: {result.evaluated_count}, Feasible: {result.feasible_count}.")
        if result.success and result.winning_candidate:
            best_vars = ", ".join(f"{k}={v}" for k, v in result.winning_candidate.design_variables.items())
            self.info(f"Winning Candidate: [{best_vars}] with Score: {result.winning_candidate.overall_score:.4f}")
        else:
            self.warning("Optimization failed to select a valid candidate.")
