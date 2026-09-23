"""
Fixed-Wing Mission Verification Strategy Subsystem

Purpose:
    Defines the `VerificationStrategy` base class and concrete verification strategies.

Role in Architecture:
    The strategy pattern isolates target compliance limits, risk bounds, and corrective remedial advice.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class VerificationStrategy(ABC):
    """
    Abstract base class for all fixed-wing mission verification strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def get_passing_bounds(self) -> Tuple[float, float]:
        """
        Returns target bounds: (min_compliance_pct, max_acceptable_risk_score).
        """
        pass

    @abstractmethod
    def get_remedial_actions(self) -> List[str]:
        """Generates advice if design checks fail compliance limits."""
        pass


class BaseVerificationStrategy(VerificationStrategy):
    """
    Common base implementation of VerificationStrategy.
    """

    def get_passing_bounds(self) -> Tuple[float, float]:
        return 85.0, 35.0

    def get_remedial_actions(self) -> List[str]:
        return [
            "Adjust battery/payload longitudinal placements inside the fuselage to correct CG offsets.",
            "Verify all autopilot parameters meet redundancy profiles.",
        ]


class LongEnduranceVerificationStrategy(BaseVerificationStrategy):
    """Strategy for long range gliders soaring at slow speeds."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def get_passing_bounds(self) -> Tuple[float, float]:
        return 88.0, 30.0  # stricter compliance on long range energy limits

    def get_remedial_actions(self) -> List[str]:
        actions = super().get_remedial_actions()
        actions.extend([
            "Select thinner airfoil profiles to reduce drag or increase wing aspect ratio to boost lift-to-drag ratios.",
        ])
        return actions


class SurveyVerificationStrategy(BaseVerificationStrategy):
    """Strategy optimized for photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Survey"

    def get_remedial_actions(self) -> List[str]:
        actions = super().get_remedial_actions()
        actions.extend([
            "Improve camera mounting vibration isolations to ensure clean camera stabilization.",
        ])
        return actions


class MappingVerificationStrategy(SurveyVerificationStrategy):
    """Strategy optimized for high-res photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Mapping"


class CargoVerificationStrategy(BaseVerificationStrategy):
    """Strategy for heavy structural load carrying."""

    @property
    def name(self) -> str:
        return "Cargo"

    def get_passing_bounds(self) -> Tuple[float, float]:
        return 90.0, 40.0  # high compliance targets but accepts slightly higher structural risks

    def get_remedial_actions(self) -> List[str]:
        actions = super().get_remedial_actions()
        actions.extend([
            "Increase motor size or reduce payload capacity to achieve safe takeoff runway rolls.",
        ])
        return actions


class TrainerVerificationStrategy(BaseVerificationStrategy):
    """Strategy optimized for crash survivability and stability."""

    @property
    def name(self) -> str:
        return "Trainer"

    def get_passing_bounds(self) -> Tuple[float, float]:
        return 80.0, 25.0  # lower compliance threshold, but risk must be very low

    def get_remedial_actions(self) -> List[str]:
        actions = super().get_remedial_actions()
        actions.extend([
            "Increase dihedral angle and tail volume coefficients to improve roll/yaw self-recovery stability.",
        ])
        return actions


class ResearchVerificationStrategy(BaseVerificationStrategy):
    """Strategy optimized for custom code execution and sensor datalogging."""

    @property
    def name(self) -> str:
        return "Research"


class BalancedVerificationStrategy(BaseVerificationStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
"""
Fixed-Wing Verification Strategy models.
"""
