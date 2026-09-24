from typing import Dict, Type
from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
from .report_strategy import (
    ReportStrategy, TechnicalReviewReportStrategy, CustomerDeliveryReportStrategy,
    PrototypeReportStrategy, ResearchReportStrategy, CertificationSupportReportStrategy,
    BalancedReportStrategy
)

class ReportRegistry:
    """
    Registry mapping mission categories to specific report formatting strategies.
    """
    _registry: Dict[VTOLMissionCategory, Type[ReportStrategy]] = {
        VTOLMissionCategory.SURVEY: CustomerDeliveryReportStrategy,
        VTOLMissionCategory.MAPPING: CustomerDeliveryReportStrategy,
        VTOLMissionCategory.CARGO: TechnicalReviewReportStrategy,
        VTOLMissionCategory.DELIVERY: CertificationSupportReportStrategy,
        VTOLMissionCategory.LONG_ENDURANCE: CertificationSupportReportStrategy,
        VTOLMissionCategory.MILITARY: CertificationSupportReportStrategy,
        VTOLMissionCategory.RESEARCH: ResearchReportStrategy,
        VTOLMissionCategory.INSPECTION: BalancedReportStrategy,
        VTOLMissionCategory.AGRICULTURE: BalancedReportStrategy,
        VTOLMissionCategory.EMERGENCY_RESPONSE: BalancedReportStrategy,
        VTOLMissionCategory.SEARCH_AND_RESCUE: BalancedReportStrategy,
        VTOLMissionCategory.CUSTOM: BalancedReportStrategy
    }

    @classmethod
    def get_strategy(cls, category: VTOLMissionCategory) -> ReportStrategy:
        strategy_class = cls._registry.get(category, BalancedReportStrategy)
        return strategy_class()
