from dataclasses import dataclass, field
from typing import Any, Dict, List

from .flight_controller_selector import FlightController
from .companion_computer import CompanionComputer
from .sensor_suite import SensorSuite
from .navigation_system import NavigationSystem
from .communication_system import CommunicationSystem
from .autonomy_stack import AutonomyStack
from .health_monitor import HealthMonitor
from .redundancy_manager import RedundancyAnalysis
from .time_synchronization import TimeSynchronization
from .avionics_analysis import AvionicsAnalysis

@dataclass(slots=True)
class AvionicsResult:
    """
    Complete sized avionics package outcome.
    """
    flight_controller: FlightController
    companion_computer: CompanionComputer
    sensor_suite: SensorSuite
    navigation_system: NavigationSystem
    communication_system: CommunicationSystem
    autonomy_stack: AutonomyStack
    health_monitor: HealthMonitor
    redundancy_analysis: RedundancyAnalysis
    time_synchronization: TimeSynchronization
    analysis: AvionicsAnalysis

    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
