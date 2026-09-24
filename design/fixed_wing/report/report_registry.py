"""
Fixed-Wing Engineering Report Strategy Registry Subsystem

Purpose:
    Defines the registry for lookup of report strategies.

Role in Architecture:
    Enables dynamic strategy selection based on target audiences.
"""

from typing import Dict, Type
from backend.design.fixed_wing.report.report_strategy import (
    ReportStrategy,
    ExecutiveReportStrategy,
    EngineeringReviewStrategy,
    ManufacturingReportStrategy,
    CertificationPreparationStrategy,
    CustomerProposalStrategy,
    ResearchReportStrategy,
    EducationalReportStrategy,
    BalancedReportStrategy,
)


class ReportStrategyRegistry:
    """
    Registry for engineering report strategies.
    """

    _registry: Dict[str, Type[ReportStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[ReportStrategy]) -> None:
        cls._registry[name.lower()] = strategy_cls

    @classmethod
    def get(cls, name: str) -> ReportStrategy:
        strategy_cls = cls._registry.get(name.lower())
        if strategy_cls is None:
            return BalancedReportStrategy()
        return strategy_cls()

    @classmethod
    def list_strategies(cls) -> list[str]:
        return list(cls._registry.keys())


# Pre-register default strategies
ReportStrategyRegistry.register("executive report", ExecutiveReportStrategy)
ReportStrategyRegistry.register("engineering review", EngineeringReviewStrategy)
ReportStrategyRegistry.register("manufacturing report", ManufacturingReportStrategy)
ReportStrategyRegistry.register("certification preparation", CertificationPreparationStrategy)
ReportStrategyRegistry.register("customer proposal", CustomerProposalStrategy)
ReportStrategyRegistry.register("research report", ResearchReportStrategy)
ReportStrategyRegistry.register("educational report", EducationalReportStrategy)
ReportStrategyRegistry.register("balanced report", BalancedReportStrategy)
