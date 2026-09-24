from typing import List
from .report_result import ReportResult
from .report_constraints import ReportConstraints

class ReportValidator:
    """
    Validates report section completeness.
    """
    @staticmethod
    def validate(result: ReportResult, constraints: ReportConstraints) -> List[str]:
        warnings = []

        # Check section count
        total_sections = (
            1 + # Exec summary
            len(result.engineering_sections) +
            len(result.performance_sections) +
            len(result.verification_sections) +
            len(result.optimization_sections) +
            len(result.cad_sections) +
            len(result.manufacturing_sections) +
            len(result.appendices)
        )
        if total_sections < constraints.min_required_sections_count:
            warnings.append(
                f"Generated report section count ({total_sections}) "
                f"is below mandatory completeness threshold ({constraints.min_required_sections_count})"
            )

        # Check traceability matrix
        if constraints.require_requirements_traceability and not result.traceability_matrix:
            warnings.append("Requirements Traceability Matrix is missing or empty in the finalized report result.")

        return warnings
