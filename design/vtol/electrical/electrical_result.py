"""
VTOL Electrical result Subsystem

Purpose:
    Defines the consolidated `ElectricalResult` dataclass outputted by the electrical stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from backend.design.vtol.electrical.battery_pack import BatteryPack
from backend.design.vtol.electrical.power_distribution import PowerDistribution
from backend.design.vtol.electrical.power_budget import PowerBudget
from backend.design.vtol.electrical.electrical_analysis import ElectricalAnalysis
from backend.design.vtol.electrical.thermal_management import ThermalAnalysis
from backend.design.vtol.electrical.charging_system import ChargingAnalysis
from backend.design.vtol.electrical.authoritative_energy import (
    AuthoritativeEnergyResult,
    MissionEnergyLedger,
    BatterySizingRequirements,
    ElectricalEnvelope,
)


@dataclass(slots=True)
class ElectricalResult:
    """
    Consolidated electrical sizing result package.

    Attributes:
        battery_selection (Dict[str, Any]): Sized cell chemistry profiles.
        battery_pack (BatteryPack): Cells configurations S/P, capacities, and weights.
        power_distribution (PowerDistribution): BECs and distribution rails.
        power_budget (PowerBudget): Subsystems power budgets.
        electrical_analysis (ElectricalAnalysis): Mission energy budgets.
        thermal_analysis (ThermalAnalysis): Heat generation and cooling requirements.
        charging_analysis (ChargingAnalysis): Charging times.
        authoritative_energy_result (Optional[AuthoritativeEnergyResult]): Phase 4 authoritative energy & sizing.
        mission_energy_ledger (Optional[MissionEnergyLedger]): Phase 4 10-phase mission energy ledger.
        battery_sizing (Optional[BatterySizingRequirements]): Phase 4 battery energy & capacity requirements.
        electrical_envelope (Optional[ElectricalEnvelope]): Phase 4 continuous & peak power/current envelope.
        engineering_notes (List[str]): Sizing observations.
        recommendations (List[str]): Downstream recommendations.
        warnings (List[str]): Safety/clearance warnings.
        metadata (Dict[str, Any]): execution timestamps.
    """

    battery_selection: Dict[str, Any]
    battery_pack: BatteryPack
    power_distribution: PowerDistribution
    power_budget: PowerBudget
    electrical_analysis: ElectricalAnalysis
    thermal_analysis: ThermalAnalysis
    charging_analysis: ChargingAnalysis
    authoritative_energy_result: AuthoritativeEnergyResult | None = None
    mission_energy_ledger: MissionEnergyLedger | None = None
    battery_sizing: BatterySizingRequirements | None = None
    electrical_envelope: ElectricalEnvelope | None = None
    engineering_notes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Recursive serialization of ElectricalResult."""
        return {
            "battery_selection": dict(self.battery_selection),
            "battery_pack": {
                "chemistry": self.battery_pack.chemistry,
                "series_count_s": self.battery_pack.series_count_s,
                "parallel_count_p": self.battery_pack.parallel_count_p,
                "capacity_ah": self.battery_pack.capacity_ah,
                "nominal_voltage_v": self.battery_pack.nominal_voltage_v,
                "energy_wh": self.battery_pack.energy_wh,
                "mass_kg": self.battery_pack.mass_kg,
                "continuous_current_limit_a": self.battery_pack.continuous_current_limit_a,
                "peak_current_limit_a": self.battery_pack.peak_current_limit_a,
            },
            "power_budget": {
                "total_hover_w": self.power_budget.total_hover_w,
                "total_cruise_w": self.power_budget.total_cruise_w,
                "total_transition_w": self.power_budget.total_transition_w,
                "reserve_energy_wh": self.power_budget.reserve_energy_wh,
            },
            "electrical_analysis": {
                "mission_energy_wh": self.electrical_analysis.mission_energy_wh,
                "hover_energy_wh": self.electrical_analysis.hover_energy_wh,
                "transition_energy_wh": self.electrical_analysis.transition_energy_wh,
                "cruise_energy_wh": self.electrical_analysis.cruise_energy_wh,
                "reserve_energy_wh": self.electrical_analysis.reserve_energy_wh,
                "battery_utilization_percent": self.electrical_analysis.battery_utilization_percent,
                "voltage_sag_v": self.electrical_analysis.voltage_sag_v,
                "current_margins_percent": self.electrical_analysis.current_margins_percent,
            },
            "thermal_analysis": {
                "hover_heat_generation_w": self.thermal_analysis.hover_heat_generation_w,
                "cruise_heat_generation_w": self.thermal_analysis.cruise_heat_generation_w,
                "estimated_pack_temp_c": self.thermal_analysis.estimated_pack_temp_c,
                "cooling_method_required": self.thermal_analysis.cooling_method_required,
            },
            "charging_analysis": {
                "charging_current_a": self.charging_analysis.charging_current_a,
                "charging_time_hr": self.charging_analysis.charging_time_hr,
            },
            "authoritative_energy_result": (
                self.authoritative_energy_result.to_dict() if self.authoritative_energy_result else None
            ),
            "mission_energy_ledger": (
                self.mission_energy_ledger.to_dict() if self.mission_energy_ledger else None
            ),
            "battery_sizing": (
                self.battery_sizing.to_dict() if self.battery_sizing else None
            ),
            "electrical_envelope": (
                self.electrical_envelope.to_dict() if self.electrical_envelope else None
            ),
            "engineering_notes": list(self.engineering_notes),
            "recommendations": list(self.recommendations),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }
