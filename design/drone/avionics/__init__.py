"""
Drone Avionics package for Torq Wings Design Studio Phase 5.4 Drone Design Studio.
"""

from backend.design.drone.avionics.communication_analysis import CommunicationAnalysis, CommunicationAnalysisResult
from backend.design.drone.avionics.power_analysis import AvionicsPowerAnalysis, AvionicsPowerAnalysisResult
from backend.design.drone.avionics.flight_controller_selector import FlightControllerSelector
from backend.design.drone.avionics.gps_selector import GpsSelector
from backend.design.drone.avionics.receiver_selector import ReceiverSelector
from backend.design.drone.avionics.telemetry_selector import TelemetrySelector
from backend.design.drone.avionics.camera_selector import CameraSelector
from backend.design.drone.avionics.companion_computer_selector import CompanionComputerSelector
from backend.design.drone.avionics.sensor_selector import SensorSelector
from backend.design.drone.avionics.avionics_profile import AvionicsProfile
from backend.design.drone.avionics.avionics_requirements import AvionicsRequirements
from backend.design.drone.avionics.avionics_constraints import AvionicsConstraints
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.avionics.avionics_validator import AvionicsValidator
from backend.design.drone.avionics.avionics_strategy import (
    AvionicsStrategy,
    BalancedStrategy,
    MappingStrategy,
    AutonomousStrategy,
)
from backend.design.drone.avionics.avionics_registry import AvionicsRegistry
from backend.design.drone.avionics.avionics_engine import AvionicsEngine

__all__ = [
    "CommunicationAnalysis",
    "CommunicationAnalysisResult",
    "AvionicsPowerAnalysis",
    "AvionicsPowerAnalysisResult",
    "FlightControllerSelector",
    "GpsSelector",
    "ReceiverSelector",
    "TelemetrySelector",
    "CameraSelector",
    "CompanionComputerSelector",
    "SensorSelector",
    "AvionicsProfile",
    "AvionicsRequirements",
    "AvionicsConstraints",
    "AvionicsResult",
    "AvionicsValidator",
    "AvionicsStrategy",
    "BalancedStrategy",
    "MappingStrategy",
    "AutonomousStrategy",
    "AvionicsRegistry",
    "AvionicsEngine",
]
