"""
Fixed-Wing Payload Strategy Subsystem

Purpose:
    Defines the `PayloadStrategy` base class and concrete selection strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates payload types, mounting methods, orientations,
    and recommendations based on mission profile.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements, PayloadType


class PayloadStrategy(ABC):
    """
    Abstract base class for all fixed-wing payload integration strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        """Determines what mission sensors/cargo should be integrated."""
        pass

    @abstractmethod
    def get_layout_guidelines(self) -> Tuple[str, str]:
        """Returns (orientation, accessibility)."""
        pass

    @abstractmethod
    def get_mount_style(self) -> str:
        """Determines the physical attachment mount style."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Generates payload integration and vibration tips."""
        pass


class BasePayloadStrategy(PayloadStrategy):
    """
    Common base implementation of PayloadStrategy.
    """

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.RGB_CAMERA]

    def get_layout_guidelines(self) -> Tuple[str, str]:
        return "Nadir Downward", "Bottom hatch canopy"

    def get_mount_style(self) -> str:
        return "Rigid floor plate with anti-vibration damping"

    def get_recommendations(self) -> List[str]:
        return [
            "Use rubber grommets to isolate high-frequency airframe engine vibration from camera lenses.",
            "Verify all cargo weights are strapped securely to prevent longitudinal sliding during nose dives.",
        ]


class LongEndurancePayloadStrategy(BasePayloadStrategy):
    """Strategy for long range soaring gliders carrying minimal weight."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.ENV_SENSORS]

    def get_layout_guidelines(self) -> Tuple[str, str]:
        return "Forward-Facing", "Nose bay hatch"


class SurveillancePayloadStrategy(BasePayloadStrategy):
    """Strategy optimized for tactical surveillance, security, and reconnaissance."""

    @property
    def name(self) -> str:
        return "Surveillance"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.RGB_CAMERA]

    def get_layout_guidelines(self) -> Tuple[str, str]:
        return "Forward / Nadir Gimbal", "Nose payload turret hatch"

    def get_mount_style(self) -> str:
        return "2-axis EO/IR gimbal turret mount"

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Isolate the camera sensor from fuselage acoustic and vibration modes using alpha-gel dampers.",
            "Ensure the forward sensor dome provides clear unobstructed pan and tilt angles.",
        ])
        return recs


class SurveyPayloadStrategy(BasePayloadStrategy):
    """Strategy optimized for photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Survey"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.RGB_CAMERA]

    def get_mount_style(self) -> str:
        return "2-axis gimbal mount with active pitch stabilization"

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Orient the camera so the lens fits cleanly within the fuselage bottom cutout window.",
            "Maintain lens glass cleanliness using a dynamic retracting hatch cover during landings.",
        ])
        return recs


class MappingPayloadStrategy(SurveyPayloadStrategy):
    """Strategy optimized for high-res photogrammetry mapping grids."""

    @property
    def name(self) -> str:
        return "Mapping"


class InspectionPayloadStrategy(BasePayloadStrategy):
    """Strategy optimized for powerline/pipeline checking using thermal sensors."""

    @property
    def name(self) -> str:
        return "Inspection"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.RGB_CAMERA, PayloadType.THERMAL]

    def get_layout_guidelines(self) -> Tuple[str, str]:
        return "Forward-Facing", "Nose payload compartment"

    def get_mount_style(self) -> str:
        return "3-axis gimbal mount with pan-tilt-zoom control"


class CargoPayloadStrategy(BasePayloadStrategy):
    """Strategy for heavy structural package hauling."""

    @property
    def name(self) -> str:
        return "Cargo"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.CARGO]

    def get_layout_guidelines(self) -> Tuple[str, str]:
        return "Internal Centered", "Sliding undercarriage bay doors"

    def get_mount_style(self) -> str:
        return "Foam cargo cavity with quick-release lock brackets"


class ResearchPayloadStrategy(BasePayloadStrategy):
    """Strategy optimized for custom sensors and probe telemetry."""

    @property
    def name(self) -> str:
        return "Research"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.SCIENTIFIC, PayloadType.ENV_SENSORS]

    def get_layout_guidelines(self) -> Tuple[str, str]:
        return "External Wing Mount", "Detachable wing pod"

    def get_mount_style(self) -> str:
        return "Rigid floor plate with clamp rings"


class AgriculturePayloadStrategy(BasePayloadStrategy):
    """Strategy optimized for crop health NDVI multispectral scans."""

    @property
    def name(self) -> str:
        return "Agriculture"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.MULTISPECTRAL]

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Calibrate the down-welling light sensor (DLS) on the upper wing surface to correct for cloud shade.",
        ])
        return recs


class EnvironmentalPayloadStrategy(BasePayloadStrategy):
    """Strategy optimized for air quality sniffing sensors."""

    @property
    def name(self) -> str:
        return "Environmental"

    def select_payloads(self, requirements: PayloadRequirements) -> List[PayloadType]:
        if requirements.preferred_payloads is not None:
            return requirements.preferred_payloads
        return [PayloadType.ENV_SENSORS]

    def get_layout_guidelines(self) -> Tuple[str, str]:
        return "External nose boom", "Nose bay hatch"


class BalancedPayloadStrategy(BasePayloadStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
