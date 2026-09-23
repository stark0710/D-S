from .report_requirements import ReportRequirements
from .report_profile import ReportProfile
from .report_constraints import ReportConstraints
from .report_result import ReportResult
from .report_registry import ReportRegistry
from .report_validator import ReportValidator

class VTOLReportEngine:
    """
    Façade manager coordinating complete VTOL aircraft report generation sheets.
    """
    def __init__(self, profile: ReportProfile = None, constraints: ReportConstraints = None):
        self.profile = profile or ReportProfile()
        self.constraints = constraints or ReportConstraints()

    def design(self, requirements: ReportRequirements) -> ReportResult:
        strategy = ReportRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.generate_report(requirements, self.profile)
        
        errors = ReportValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
