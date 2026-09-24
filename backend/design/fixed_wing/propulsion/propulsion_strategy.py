"""
Fixed-Wing Propulsion Strategy Subsystem

Purpose:
    Defines the `PropulsionStrategy` base class and concrete selection strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates target thrust-to-weight ratios, motor layouts, and propulsion styles
    (Electric, ICE, Hybrid) based on mission type.
"""

from abc import ABC, abstractmethod
from typing import List
from backend.design.fixed_wing.propulsion.propulsion_requirements import (
    PropulsionRequirements,
    PropulsionType,
    PropulsionLayout,
)


class PropulsionStrategy(ABC):
    """
    Abstract base class for all fixed-wing propulsion selection strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def select_propulsion_type(self, requirements: PropulsionRequirements) -> PropulsionType:
        """Determines the propulsion power source type."""
        pass

    @abstractmethod
    def select_propulsion_layout(self, requirements: PropulsionRequirements) -> PropulsionLayout:
        """Determines the layout configuration of motors/engines."""
        pass

    @abstractmethod
    def get_thrust_to_weight_ratio(self) -> float:
        """Target thrust-to-weight ratio for flight stability and climb."""
        pass

    @abstractmethod
    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        """Generates detailed propulsion and propeller design advice."""
        pass


class BasePropulsionStrategy(PropulsionStrategy):
    """
    Common base implementation of PropulsionStrategy.
    """

    def select_propulsion_type(self, requirements: PropulsionRequirements) -> PropulsionType:
        if requirements.preferred_propulsion_type is not None:
            return requirements.preferred_propulsion_type
        return PropulsionType.ELECTRIC

    def select_propulsion_layout(self, requirements: PropulsionRequirements) -> PropulsionLayout:
        if requirements.preferred_layout is not None:
            return requirements.preferred_layout

        # Fallback to configuration selection layout
        layout = requirements.configuration_result.selected_configuration
        prop_val = layout.get("propulsion_layout", "")
        
        # Match config string to enum
        for style in PropulsionLayout:
            if style.value.lower() == prop_val.lower():
                return style
            if prop_val.lower() == "tractor":
                return PropulsionLayout.SINGLE_TRACTOR
            if prop_val.lower() == "pusher":
                return PropulsionLayout.SINGLE_PUSHER
                
        return PropulsionLayout.SINGLE_TRACTOR

    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        return [
            "Balance the propeller blade before flight to eliminate high-frequency motor mount vibration.",
            "Verify ESC voltage matches nominal motor battery voltage to avoid overheating components.",
        ]


class LongEndurancePropulsionStrategy(BasePropulsionStrategy):
    """Strategy optimized for low power draw and maximum powertrain efficiency."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def select_propulsion_type(self, requirements: PropulsionRequirements) -> PropulsionType:
        if requirements.preferred_propulsion_type is not None:
            return requirements.preferred_propulsion_type
        # Hybrid is excellent for long duration, but default is Electric
        return PropulsionType.ELECTRIC

    def get_thrust_to_weight_ratio(self) -> float:
        return 0.40  # lower thrust-to-weight saves weight and minimizes battery draw

    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        recs = super().get_recommendations(thrust_ratio)
        recs.extend([
            "Select high-diameter, low-pitch folding propellers to minimize drag during soaring glide phases.",
            "Utilize a low-KV motor at 6S/12S to maintain high efficiency and keep wire resistive heat low.",
        ])
        return recs


class SurveyPropulsionStrategy(BasePropulsionStrategy):
    """Strategy optimized for quiet and stable grid tracking."""

    @property
    def name(self) -> str:
        return "Survey"

    def get_thrust_to_weight_ratio(self) -> float:
        return 0.50

    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        recs = super().get_recommendations(thrust_ratio)
        recs.extend([
            "Pusher layouts keep camera lens clean of oil or propeller dust. Ensure rear blades have spinner cones.",
        ])
        return recs


class CargoPropulsionStrategy(BasePropulsionStrategy):
    """Strategy optimized for maximum thrust lift capabilities."""

    @property
    def name(self) -> str:
        return "Cargo"

    def select_propulsion_type(self, requirements: PropulsionRequirements) -> PropulsionType:
        if requirements.preferred_propulsion_type is not None:
            return requirements.preferred_propulsion_type
        # ICE is preferred for large heavy cargo due to high energy density of gasoline
        m_profile = requirements.mission_result.mission_profile
        if m_profile.payload_kg >= 5.0:
            return PropulsionType.ICE
        return PropulsionType.ELECTRIC

    def select_propulsion_layout(self, requirements: PropulsionRequirements) -> PropulsionLayout:
        if requirements.preferred_layout is not None:
            return requirements.preferred_layout
        m_profile = requirements.mission_result.mission_profile
        if m_profile.payload_kg >= 4.0:
            return PropulsionLayout.TWIN_TRACTOR  # Twin motors for heavy lift torque balancing
        return PropulsionLayout.SINGLE_TRACTOR

    def get_thrust_to_weight_ratio(self) -> float:
        return 0.70  # High thrust-to-weight to climb safely at MTOW

    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        recs = super().get_recommendations(thrust_ratio)
        recs.extend([
            "For heavy lifters, use twin counter-rotating propellers to eliminate spiralling slipstream torque roll.",
            "Verify engine firewall is secured with heavy aircraft bolts and locking nylon nuts.",
        ])
        return recs


class TrainerPropulsionStrategy(BasePropulsionStrategy):
    """Strategy optimized for docile throttle response."""

    @property
    def name(self) -> str:
        return "Trainer"

    def get_thrust_to_weight_ratio(self) -> float:
        return 0.55

    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        recs = super().get_recommendations(thrust_ratio)
        recs.extend([
            "Set throttle limit brackets to 75% in the radio controller to prevent trainees from over-speeding.",
        ])
        return recs


class HighSpeedPropulsionStrategy(BasePropulsionStrategy):
    """Strategy optimized for maximum dash speeds and high-rate climbs."""

    @property
    def name(self) -> str:
        return "High Speed"

    def get_thrust_to_weight_ratio(self) -> float:
        return 1.10  # T/W > 1.0 allows vertical climb capability!

    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        recs = super().get_recommendations(thrust_ratio)
        recs.extend([
            "Select high-pitch propellers (pitch-to-diameter ratio >= 0.8) to maintain thrust at high dash speeds.",
            "Provide ample cooling airflow past the ESC to prevent thermal cutoff during full-throttle sprints.",
        ])
        return recs


class BalancedPropulsionStrategy(BasePropulsionStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"

    def get_thrust_to_weight_ratio(self) -> float:
        return 0.50

    def get_recommendations(self, thrust_ratio: float) -> List[str]:
        recs = super().get_recommendations(thrust_ratio)
        return recs
