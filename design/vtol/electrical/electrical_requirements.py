"""
VTOL Electrical Requirements Subsystem

Purpose:
    Defines the `ElectricalRequirements` class capturing layout design overrides
    and preceding stage outputs for the electrical sizing stage.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from backend.design.vtol.mission.mission_result import MissionResult
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.wing.wing_result import WingResult
from backend.design.vtol.airfoil.airfoil_result import AirfoilResult
from backend.design.vtol.tail.tail_result import TailResult
from backend.design.vtol.fuselage.fuselage_result import FuselageResult
from backend.design.vtol.lift_system.lift_system_result import LiftSystemResult
from backend.design.vtol.forward_propulsion.forward_propulsion_result import ForwardPropulsionResult


@dataclass(slots=True)
class ElectricalRequirements:
    """
    Inputs for VTOL electrical system and battery sizing.

    Attributes:
        mission_result (MissionResult): Sized mission profile.
        configuration_result (ConfigurationResult): Layout configuration.
        wing_result (WingResult): Sized wing.
        airfoil_result (AirfoilResult): Selected airfoil.
        tail_result (TailResult): Sized stabilizer tail.
        fuselage_result (FuselageResult): Sized fuselage layout.
        lift_system_result (LiftSystemResult): Sized hover lift systems.
        forward_propulsion_result (ForwardPropulsionResult): Sized forward flight drive train.
        preferred_battery_chemistry (str | None): Preferred chemistry override (e.g. LiPo, Li-Ion).
        preferred_series_count (int | None): Preferred series cell count (S) override.
        preferred_parallel_count (int | None): Preferred parallel cell count (P) override.
        metadata (Dict[str, Any]): Additional override flags or target settings.
    """

    mission_result: MissionResult
    configuration_result: ConfigurationResult
    wing_result: WingResult
    airfoil_result: AirfoilResult
    tail_result: TailResult
    fuselage_result: FuselageResult
    lift_system_result: LiftSystemResult
    forward_propulsion_result: ForwardPropulsionResult
    hover_performance_result: Any | None = None
    transition_result: Any | None = None
    reverse_transition_result: Any | None = None
    cruise_performance_result: Any | None = None
    fixed_wing_subsystems: Any | None = None
    preferred_battery_chemistry: str | None = None
    preferred_series_count: int | None = None
    preferred_parallel_count: int | None = None
    preferred_nominal_voltage_v: float | None = None
    preferred_reserve_fraction: float | None = None
    preferred_usable_fraction: float | None = None
    specific_energy_wh_kg: float | None = None
    max_allowable_c_rate: float | None = None
    avionics_result: Any | None = None
    payload_result: Any | None = None
    preferred_avionics_power_w: float | None = None
    preferred_payload_power_w: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)
