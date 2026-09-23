"""
VTOL Electrical Strategy Subsystem

Purpose:
    Defines the `ElectricalStrategy` abstract base and concrete implementations
    specifying battery chemistries and climb safety factors.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class ElectricalStrategy(ABC):
    """
    Interface for VTOL electrical system strategies.
    """

    @property
    @abstractmethod
    def category(self) -> Any:
        pass

    @property
    @abstractmethod
    def default_chemistry(self) -> str:
        """Sized battery chemistry."""
        pass

    @property
    @abstractmethod
    def default_reserve_factor(self) -> float:
        """Reserve factor sizing multiplier."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Sizing recommendations."""
        pass


class BaseElectricalStrategy(ElectricalStrategy):
    """
    Generic electrical strategies.
    """

    @property
    def default_chemistry(self) -> str:
        return "LiHV"

    @property
    def default_reserve_factor(self) -> float:
        return 1.20

    def get_recommendations(self) -> List[str]:
        return [
            "Use heavy AWG power cables to minimize heating and voltage drops.",
            "Install a hall-effect power sensor to log real-time current telemetry.",
        ]


class SurveyElectricalStrategy(BaseElectricalStrategy):
    """Camera scans require high discharge currents to cover hover segments."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.SURVEY

    @property
    def default_chemistry(self) -> str:
        return "LiHV"

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Employ dual-bus BEC modules to separate radio links from motor noise spikes.",
        ])
        return recs


class CargoElectricalStrategy(BaseElectricalStrategy):
    """Heavy cargo requires high-current LiPo packs."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CARGO

    @property
    def default_chemistry(self) -> str:
        return "LiPo"

    @property
    def default_reserve_factor(self) -> float:
        return 1.25

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use high C-rate (45C+) LiPo packs to handle massive hover power demands.",
            "Add dual structural fuses on the main battery positive lead.",
        ])
        return recs


class MappingElectricalStrategy(BaseElectricalStrategy):
    """Stable mapping scans."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MAPPING

    @property
    def default_chemistry(self) -> str:
        return "LiHV"

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class LongEnduranceElectricalStrategy(BaseCruiseStrategy if 'BaseCruiseStrategy' in globals() else BaseElectricalStrategy):
    """Endurance requires high Wh/kg Li-Ion cells."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.LONG_ENDURANCE

    @property
    def default_chemistry(self) -> str:
        return "Li-Ion"

    @property
    def default_reserve_factor(self) -> float:
        return 1.15

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use high capacity Li-Ion cells in 18650/21700 S/P configuration to maximize range.",
            "Monitor cell temperatures closely as Li-Ion lacks high thermal cooling dissipation.",
        ])
        return recs


class MilitaryElectricalStrategy(BaseElectricalStrategy):
    """Agility and high-speed discharge focus."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.MILITARY

    @property
    def default_chemistry(self) -> str:
        return "LiPo"

    @property
    def default_reserve_factor(self) -> float:
        return 1.30

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class ResearchElectricalStrategy(BaseElectricalStrategy):
    """Flexible research setups."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.RESEARCH

    @property
    def default_chemistry(self) -> str:
        return "LiHV"

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()


class BalancedElectricalStrategy(BaseElectricalStrategy):
    """Balanced generic custom category."""

    @property
    def category(self) -> Any:
        from backend.design.vtol.mission.mission_requirements import VTOLMissionCategory
        return VTOLMissionCategory.CUSTOM

    def get_recommendations(self) -> List[str]:
        return super().get_recommendations()
