"""
Drone Electrical package for Torq Wings Design Studio Phase 5.4 Drone Design Studio.
"""

from backend.design.drone.electrical.power_budget import PowerBudget
from backend.design.drone.electrical.current_analysis import CurrentAnalysis, CurrentAnalysisResult
from backend.design.drone.electrical.voltage_analysis import VoltageAnalysis, VoltageAnalysisResult
from backend.design.drone.electrical.efficiency_analysis import EfficiencyAnalysis
from backend.design.drone.electrical.battery_selector import BatterySelector
from backend.design.drone.electrical.esc_selector import EscSelector
from backend.design.drone.electrical.pdb_selector import PdbSelector
from backend.design.drone.electrical.bec_selector import BecSelector
from backend.design.drone.electrical.connector_selector import ConnectorSelector
from backend.design.drone.electrical.wire_selector import WireSelector
from backend.design.drone.electrical.electrical_profile import ElectricalProfile
from backend.design.drone.electrical.electrical_requirements import ElectricalRequirements
from backend.design.drone.electrical.electrical_constraints import ElectricalConstraints
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.electrical.electrical_validator import ElectricalValidator
from backend.design.drone.electrical.electrical_strategy import (
    ElectricalStrategy,
    BalancedStrategy,
    LongEnduranceStrategy,
)
from backend.design.drone.electrical.electrical_registry import ElectricalRegistry
from backend.design.drone.electrical.electrical_engine import ElectricalEngine

__all__ = [
    "PowerBudget",
    "CurrentAnalysis",
    "CurrentAnalysisResult",
    "VoltageAnalysis",
    "VoltageAnalysisResult",
    "EfficiencyAnalysis",
    "BatterySelector",
    "EscSelector",
    "PdbSelector",
    "BecSelector",
    "ConnectorSelector",
    "WireSelector",
    "ElectricalProfile",
    "ElectricalRequirements",
    "ElectricalConstraints",
    "ElectricalResult",
    "ElectricalValidator",
    "ElectricalStrategy",
    "BalancedStrategy",
    "LongEnduranceStrategy",
    "ElectricalRegistry",
    "ElectricalEngine",
]
