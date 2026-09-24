"""
Fixed-Wing Avionics Engineering Framework Package Entry Point

Purpose:
    Exposes the public interfaces, domain models, and orchestrators of the
    Fixed-Wing Avionics Engineering Framework.
"""

from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements, AutopilotFirmware, GNSSConfiguration
from backend.design.fixed_wing.avionics.avionics_profile import AvionicsProfile
from backend.design.fixed_wing.avionics.avionics_constraints import AvionicsConstraints
from backend.design.fixed_wing.avionics.avionics_result import AvionicsResult
from backend.design.fixed_wing.avionics.avionics_validator import AvionicsValidator, AvionicsValidationError
from backend.design.fixed_wing.avionics.flight_controller_selector import FlightControllerSelector, FlightControllerRecord
from backend.design.fixed_wing.avionics.gps_selector import GPSSelector, GPSRecord
from backend.design.fixed_wing.avionics.receiver_selector import ReceiverSelector, ReceiverRecord
from backend.design.fixed_wing.avionics.telemetry_selector import TelemetrySelector, TelemetryRecord
from backend.design.fixed_wing.avionics.camera_selector import CameraSelector, CameraRecord
from backend.design.fixed_wing.avionics.companion_computer_selector import CompanionComputerSelector, CompanionComputerRecord
from backend.design.fixed_wing.avionics.sensor_selector import SensorSelector, SensorRecord
from backend.design.fixed_wing.avionics.navigation_analysis import NavigationAnalysis
from backend.design.fixed_wing.avionics.communication_analysis import CommunicationAnalysis
from backend.design.fixed_wing.avionics.power_analysis import PowerAnalysis
from backend.design.fixed_wing.avionics.avionics_strategy import AvionicsStrategy
from backend.design.fixed_wing.avionics.avionics_registry import AvionicsStrategyRegistry
from backend.design.fixed_wing.avionics.avionics_engine import AvionicsEngine

__all__ = [
    "AvionicsRequirements",
    "AutopilotFirmware",
    "GNSSConfiguration",
    "AvionicsProfile",
    "AvionicsConstraints",
    "AvionicsResult",
    "AvionicsValidator",
    "AvionicsValidationError",
    "FlightControllerSelector",
    "FlightControllerRecord",
    "GPSSelector",
    "GPSRecord",
    "ReceiverSelector",
    "ReceiverRecord",
    "TelemetrySelector",
    "TelemetryRecord",
    "CameraSelector",
    "CameraRecord",
    "CompanionComputerSelector",
    "CompanionComputerRecord",
    "SensorSelector",
    "SensorRecord",
    "NavigationAnalysis",
    "CommunicationAnalysis",
    "PowerAnalysis",
    "AvionicsStrategy",
    "AvionicsStrategyRegistry",
    "AvionicsEngine",
]
