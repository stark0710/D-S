"""
Fixed-Wing Flight Performance Strategy Subsystem

Purpose:
    Defines the `FlightStrategy` base class and concrete selection strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates safety speed margins, climb rate bounds, and recommendations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class FlightStrategy(ABC):
    """
    Abstract base class for all fixed-wing flight performance strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_performance_margins(self) -> Tuple[float, float]:
        """
        Returns target margins: (minimum_rate_of_climb_m_s, cruise_speed_margin_above_stall_pct).
        """
        pass

    @abstractmethod
    def get_stall_speed_margin_pct(self) -> float:
        """Required safety buffer above stall speed for approach/rotation."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Generates performance flight advice."""
        pass


class BaseFlightStrategy(FlightStrategy):
    """
    Common base implementation of FlightStrategy.
    """

    def get_performance_margins(self) -> Tuple[float, float]:
        return 2.0, 30.0

    def get_stall_speed_margin_pct(self) -> float:
        return 30.0

    def get_recommendations(self) -> List[str]:
        return [
            "Perform pre-flight range checks on telemetry links to verify radio coverage margins.",
            "Verify flap settings are correctly mapped in the ground control station to lower stall speeds.",
        ]


class LongEnduranceFlightStrategy(BaseFlightStrategy):
    """Strategy for long range gliders carrying minimal weight and soaring at low speeds."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def get_performance_margins(self) -> Tuple[float, float]:
        return 1.5, 20.0  # low climb rate is fine, slow cruise speeds save battery

    def get_stall_speed_margin_pct(self) -> float:
        return 25.0

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Fly at the best-endurance speed (minimum power required speed) to maximize flight duration.",
        ])
        return recs


class SurveyFlightStrategy(BaseFlightStrategy):
    """Strategy optimized for photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Survey"

    def get_performance_margins(self) -> Tuple[float, float]:
        return 1.5, 20.0

    def get_stall_speed_margin_pct(self) -> float:
        return 20.0

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Ensure grid lines are aligned with prevailing wind directions to maintain stable camera angles.",
        ])
        return recs


class MappingFlightStrategy(SurveyFlightStrategy):
    """Strategy optimized for high-res photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Mapping"


class CargoFlightStrategy(BaseFlightStrategy):
    """Strategy for heavy structural load carrying."""

    @property
    def name(self) -> str:
        return "Cargo"

    def get_performance_margins(self) -> Tuple[float, float]:
        return 3.0, 35.0  # high rate of climb margin required to lift full load safely

    def get_stall_speed_margin_pct(self) -> float:
        return 35.0  # high safety margin above stall to handle gusts

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Avoid bank angles exceeding 30 degrees when flying near MTOW to prevent structural stall acceleration.",
        ])
        return recs


class TrainerFlightStrategy(BaseFlightStrategy):
    """Strategy optimized for crash survivability and stability."""

    @property
    def name(self) -> str:
        return "Trainer"

    def get_stall_speed_margin_pct(self) -> float:
        return 40.0  # extremely safe speed margin to prevent trainees from stalling

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Set cruise throttle limits to docilize response and extend student reaction windows.",
        ])
        return recs


class HighSpeedFlightStrategy(BaseFlightStrategy):
    """Strategy optimized for high-rate climbs and dash speeds."""

    @property
    def name(self) -> str:
        return "High Speed"

    def get_performance_margins(self) -> Tuple[float, float]:
        return 5.0, 60.0  # high speed and aggressive climbs

    def get_stall_speed_margin_pct(self) -> float:
        return 20.0

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Select high-pitch props to ensure thrust does not drop off at high dash speeds.",
        ])
        return recs


class ResearchFlightStrategy(BaseFlightStrategy):
    """Strategy optimized for custom code execution and sensor datalogging."""

    @property
    def name(self) -> str:
        return "Research"


class BalancedFlightStrategy(BaseFlightStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
"""
Fixed-Wing Flight Strategy models.
"""
