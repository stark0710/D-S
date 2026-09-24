"""
Pipeline Diagnostics extraction tool.
"""
from typing import Dict, Any
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext


class PipelineDiagnostics:
    @staticmethod
    def extract_diagnostics(context: FixedWingPipelineContext) -> Dict[str, Any]:
        """Extracts sizing convergence metrics and execution statistics."""
        diag = {
            "errors": context.errors,
            "warnings": context.warnings,
            "execution_metadata": context.execution_metadata,
            "iteration_count": len(context.iteration_history),
            "certification_status": context.certification_status,
        }
        if context.certification_report:
            diag["certification_score"] = context.certification_report.certification_score
        return diag
