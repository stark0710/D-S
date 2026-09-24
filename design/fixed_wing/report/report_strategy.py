"""
Fixed-Wing Engineering Report Strategy Subsystem

Purpose:
    Defines the `ReportStrategy` base class and concrete selection strategies.

Role in Architecture:
    The strategy pattern isolates target sections, detail levels, and formatting recommendations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class ReportStrategy(ABC):
    """
    Abstract base class for all fixed-wing report strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_sections_list(self) -> List[str]:
        """Returns list of chapters to compile based on target audience."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Generates reporting recommendations."""
        pass


class BaseReportStrategy(ReportStrategy):
    """
    Common base implementation of ReportStrategy.
    """

    def get_sections_list(self) -> List[str]:
        return [
            "Executive Summary",
            "Mission Overview",
            "Configuration",
            "Wing Geometry",
            "Airfoil Selection",
            "Tail Empennage",
            "Fuselage Packaging",
            "Propulsion System",
            "Flight Performance",
            "Mission Verification",
            "CAD Output",
            "Manufacturing Package",
            "Engineering Recommendations",
        ]

    def get_recommendations(self) -> List[str]:
        return [
            "Verify all CAD drawings match manufacturing BOM entries.",
            "Verify stability margins are verified before test flights.",
        ]


class ExecutiveReportStrategy(BaseReportStrategy):
    """Strategy optimized for project stakeholders and commercial managers."""

    @property
    def name(self) -> str:
        return "Executive Summary Strategy"

    def get_sections_list(self) -> List[str]:
        return [
            "Executive Summary",
            "Mission Overview",
            "Configuration",
            "Flight Performance",
            "CAD Output",
            "Manufacturing Package",
            "Engineering Recommendations",
        ]

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Focus on ROI, unit costs, and mission capabilities metrics.",
        ])
        return recs


class EngineeringReviewStrategy(BaseReportStrategy):
    """Strategy optimized for peer design reviews and certification audits."""

    @property
    def name(self) -> str:
        return "Engineering Review Strategy"

    def get_sections_list(self) -> List[str]:
        # Compile all chapters
        sections = super().get_sections_list()
        sections.extend(["Avionics Redundancy", "Mass Properties & CG", "Appendix"])
        return sections


class ManufacturingReportStrategy(BaseReportStrategy):
    """Strategy optimized for shop-floor mechanics and cutting operators."""

    @property
    def name(self) -> str:
        return "Manufacturing Strategy"

    def get_sections_list(self) -> List[str]:
        return [
            "Executive Summary",
            "Wing Geometry",
            "Fuselage Packaging",
            "CAD Output",
            "Manufacturing Package",
            "Engineering Recommendations",
        ]


class CertificationPreparationStrategy(BaseReportStrategy):
    """Strategy optimized for civil aviation authority submissions."""

    @property
    def name(self) -> str:
        return "Certification Preparation Strategy"

    def get_sections_list(self) -> List[str]:
        sections = super().get_sections_list()
        sections.extend(["Avionics Redundancy", "Flight Safety Checks"])
        return sections


class CustomerProposalStrategy(BaseReportStrategy):
    """Strategy optimized for customer proposals."""

    @property
    def name(self) -> str:
        return "Customer Proposal"


class ResearchReportStrategy(BaseReportStrategy):
    """Strategy optimized for custom code checks."""

    @property
    def name(self) -> str:
        return "Research"


class EducationalReportStrategy(BaseReportStrategy):
    """Strategy optimized for student project submissions."""

    @property
    def name(self) -> str:
        return "Educational"

    def get_sections_list(self) -> List[str]:
        return [
            "Executive Summary",
            "Mission Overview",
            "Wing Geometry",
            "Tail Empennage",
            "Flight Performance",
            "Appendix",
        ]


class BalancedReportStrategy(BaseReportStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
"""
Fixed-Wing Engineering Report Strategy models.
"""
