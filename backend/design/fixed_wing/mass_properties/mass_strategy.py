"""
Fixed-Wing Mass Strategy Subsystem

Purpose:
    Defines the `MassStrategy` base class and concrete selection strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates target weight fractions, static margin limits,
    and recommendations based on mission profile.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class MassStrategy(ABC):
    """
    Abstract base class for all fixed-wing mass strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_target_fractions(self) -> Tuple[float, float, float]:
        """
        Returns target ratios: (structural_fraction, battery_fraction, payload_fraction)
        relative to maximum takeoff weight.
        """
        pass

    @abstractmethod
    def get_target_static_margin(self) -> Tuple[float, float]:
        """
        Returns target longitudinal stability margins: (min_margin, max_margin)
        as fraction of MAC.
        """
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Generates mass budgeting and loading advice."""
        pass


class BaseMassStrategy(MassStrategy):
    """
    Common base implementation of MassStrategy.
    """

    def get_target_fractions(self) -> Tuple[float, float, float]:
        return 0.45, 0.35, 0.20

    def get_target_static_margin(self) -> Tuple[float, float]:
        return 0.10, 0.20

    def get_recommendations(self) -> List[str]:
        return [
            "Conduct empty weight audits before flight to adjust trim positions in the autopilot.",
            "Verify all heavy batteries are strapped near the center of gravity to avoid large yaw inertia changes.",
        ]


class LongEnduranceMassStrategy(BaseMassStrategy):
    """Strategy for long range gliders carrying minimal payload and heavy battery packs."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def get_target_fractions(self) -> Tuple[float, float, float]:
        # High battery fraction, low payload fraction
        return 0.35, 0.55, 0.10

    def get_target_static_margin(self) -> Tuple[float, float]:
        # Aft CG (low static margin) saves energy by reducing down-force trim drag
        return 0.07, 0.15

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Design composite skins with thin walls to optimize structural weight fraction.",
        ])
        return recs


class SurveyMassStrategy(BaseMassStrategy):
    """Strategy optimized for photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Survey"

    def get_target_fractions(self) -> Tuple[float, float, float]:
        return 0.45, 0.35, 0.20

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Check that camera gimbals do not contact fuselage bulkheads during full pitch pan excursions.",
        ])
        return recs


class MappingMassStrategy(SurveyMassStrategy):
    """Strategy optimized for high-res photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Mapping"


class CargoMassStrategy(BaseMassStrategy):
    """Strategy for heavy structural load carrying."""

    @property
    def name(self) -> str:
        return "Cargo"

    def get_target_fractions(self) -> Tuple[float, float, float]:
        # High payload fraction, low battery/fuel fraction
        return 0.40, 0.20, 0.40

    def get_target_static_margin(self) -> Tuple[float, float]:
        # High static margin creates a stiffer aircraft, safer for heavy weight drops
        return 0.12, 0.22

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Install structural bulkheads near the payload bay to prevent skin buckling under maximum load.",
        ])
        return recs


class ResearchMassStrategy(BaseMassStrategy):
    """Strategy optimized for modular sensors weight budgets."""

    @property
    def name(self) -> str:
        return "Research"

    def get_target_fractions(self) -> Tuple[float, float, float]:
        return 0.50, 0.30, 0.20


class TrainerMassStrategy(BaseMassStrategy):
    """Strategy optimized for crash survivability and stability."""

    @property
    def name(self) -> str:
        return "Trainer"

    def get_target_fractions(self) -> Tuple[float, float, float]:
        # Heavy structure (thick balsa/EPO foam), low battery
        return 0.55, 0.30, 0.15

    def get_target_static_margin(self) -> Tuple[float, float]:
        # Forward CG (high static margin) creates highly stable docile pitch characteristics
        return 0.15, 0.25


class BalancedMassStrategy(BaseMassStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
