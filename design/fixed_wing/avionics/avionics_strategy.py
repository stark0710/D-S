"""
Fixed-Wing Avionics Strategy Subsystem

Purpose:
    Defines the `AvionicsStrategy` base class and concrete selection strategies for various aircraft missions.

Role in Architecture:
    The strategy pattern isolates target ranges, GNSS styles, flight controller choices,
    and companion computer options based on mission type.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements, AutopilotFirmware, GNSSConfiguration


class AvionicsStrategy(ABC):
    """
    Abstract base class for all fixed-wing avionics strategies.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy."""
        pass

    @abstractmethod
    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        """Returns (flight_controller_name, firmware)."""
        pass

    @abstractmethod
    def select_navigation(self, requirements: AvionicsRequirements) -> Tuple[GNSSConfiguration, int]:
        """Returns (gnss_type, redundancy_count)."""
        pass

    @abstractmethod
    def get_communication_targets(self) -> Tuple[float, bool]:
        """Returns (target_range_km, needs_video_link)."""
        pass

    @abstractmethod
    def needs_companion_computer(self) -> Tuple[bool, bool]:
        """Returns (needs_visual_nav, needs_high_ai)."""
        pass

    @abstractmethod
    def get_recommendations(self) -> List[str]:
        """Generates detailed avionics and navigation advice."""
        pass


class BaseAvionicsStrategy(AvionicsStrategy):
    """
    Common base implementation of AvionicsStrategy.
    """

    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        fc = requirements.preferred_flight_controller or "Holybro Pixhawk 6C"
        fw = requirements.preferred_firmware or AutopilotFirmware.ARDUPILOT
        return fc, fw

    def select_navigation(self, requirements: AvionicsRequirements) -> Tuple[GNSSConfiguration, int]:
        return GNSSConfiguration.SINGLE_GNSS, 1

    def get_communication_targets(self) -> Tuple[float, bool]:
        return 5.0, False

    def needs_companion_computer(self) -> Tuple[bool, bool]:
        return False, False

    def get_recommendations(self) -> List[str]:
        return [
            "Use shielding tape around GPS wires to prevent electromagnetic noise from companion computers.",
            "Install a dedicated airspeed sensor heater (pitot heat) if flying in freezing or humid clouds.",
        ]


class LongEnduranceAvionicsStrategy(BaseAvionicsStrategy):
    """Strategy optimized for low power consumption and robust telemetry."""

    @property
    def name(self) -> str:
        return "Long Endurance"

    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        fc = requirements.preferred_flight_controller or "Cube Orange+"
        fw = requirements.preferred_firmware or AutopilotFirmware.PX4  # PX4 is highly optimized for gliders
        return fc, fw

    def select_navigation(self, requirements: AvionicsRequirements) -> Tuple[GNSSConfiguration, int]:
        return GNSSConfiguration.DUAL_GNSS, 2

    def get_communication_targets(self) -> Tuple[float, bool]:
        return 40.0, False  # low-bandwidth long-range telemetry modem saves power

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use dual GNSS receivers with blending enabled to safeguard against satellite signal masking during banking.",
            "Keep companion computers powered off during cruise to optimize battery endurance.",
        ])
        return recs


class SurveyAvionicsStrategy(BaseAvionicsStrategy):
    """Strategy optimized for photogrammetry and geotagging accuracy."""

    @property
    def name(self) -> str:
        return "Survey"

    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        fc = requirements.preferred_flight_controller or "Holybro Pixhawk 6X"
        fw = requirements.preferred_firmware or AutopilotFirmware.ARDUPILOT  # ArduPilot has excellent survey auto-grid modes
        return fc, fw

    def select_navigation(self, requirements: AvionicsRequirements) -> Tuple[GNSSConfiguration, int]:
        return GNSSConfiguration.RTK_GNSS, 2  # RTK is mandatory for centimeter geotags

    def get_communication_targets(self) -> Tuple[float, bool]:
        return 10.0, True  # needs camera video feed back to base

    def needs_companion_computer(self) -> Tuple[bool, bool]:
        return True, False  # Raspberry Pi 4 is sufficient to interface with mapping camera

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Configure RTK Inject in QGroundControl to send RTK corrections to the UAV via the telemetry link.",
        ])
        return recs


class CargoAvionicsStrategy(BaseAvionicsStrategy):
    """Strategy optimized for triple redundant failsafes for large transport UAVs."""

    @property
    def name(self) -> str:
        return "Cargo"

    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        fc = requirements.preferred_flight_controller or "Holybro Pixhawk 6X"  # Pixhawk 6X is triple-redundant
        fw = requirements.preferred_firmware or AutopilotFirmware.ARDUPILOT
        return fc, fw

    def select_navigation(self, requirements: AvionicsRequirements) -> Tuple[GNSSConfiguration, int]:
        return GNSSConfiguration.DUAL_GNSS, 2

    def get_communication_targets(self) -> Tuple[float, bool]:
        return 20.0, False

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Install redundant dual BECs (Battery Eliminator Circuits) from separate battery packs to power the FC.",
            "Set failsafe options to automatically land if RC connection is lost for more than 20 seconds.",
        ])
        return recs


class TrainerAvionicsStrategy(BaseAvionicsStrategy):
    """Strategy optimized for simplicity and low cost."""

    @property
    def name(self) -> str:
        return "Trainer"

    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        fc = requirements.preferred_flight_controller or "Matek H743-WING"
        fw = requirements.preferred_firmware or AutopilotFirmware.ARDUPILOT
        return fc, fw

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Matek H743 has direct solder pads, simplifying wiring. Use heat-shrink tubing on all connections.",
        ])
        return recs


class BVLOSAvionicsStrategy(BaseAvionicsStrategy):
    """Strategy optimized for long distance remote operations."""

    @property
    def name(self) -> str:
        return "BVLOS"

    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        fc = requirements.preferred_flight_controller or "Holybro Pixhawk 6X"
        fw = requirements.preferred_firmware or AutopilotFirmware.PX4
        return fc, fw

    def select_navigation(self, requirements: AvionicsRequirements) -> Tuple[GNSSConfiguration, int]:
        return GNSSConfiguration.RTK_GNSS, 2

    def get_communication_targets(self) -> Tuple[float, bool]:
        return 60.0, True

    def needs_companion_computer(self) -> Tuple[bool, bool]:
        return True, True  # Jetson Orin Nano for computer vision obstacle avoidance

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use dual telemetry links (e.g. RFD900 + LTE backup modems) to ensure connectivity beyond line of sight.",
        ])
        return recs


class ResearchAvionicsStrategy(BaseAvionicsStrategy):
    """Strategy optimized for custom code execution and sensor datalogging."""

    @property
    def name(self) -> str:
        return "Research"

    def select_autopilot(self, requirements: AvionicsRequirements) -> Tuple[str, AutopilotFirmware]:
        fc = requirements.preferred_flight_controller or "Holybro Pixhawk 6X"
        fw = requirements.preferred_firmware or AutopilotFirmware.ARDUPILOT
        return fc, fw

    def select_navigation(self, requirements: AvionicsRequirements) -> Tuple[GNSSConfiguration, int]:
        return GNSSConfiguration.DUAL_GNSS, 2

    def get_communication_targets(self) -> Tuple[float, bool]:
        return 5.0, True

    def needs_companion_computer(self) -> Tuple[bool, bool]:
        return True, True  # NVIDIA Jetson Orin NX for high computation

    def get_recommendations(self) -> List[str]:
        recs = super().get_recommendations()
        recs.extend([
            "Use high-speed SPI/Ethernet channels to stream raw IMU telemetry data to the companion computer.",
        ])
        return recs


class BalancedAvionicsStrategy(BaseAvionicsStrategy):
    """Default balanced strategy for general UAV operations."""

    @property
    def name(self) -> str:
        return "Balanced"
