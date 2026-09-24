"""
Stress Scenario Generator for Vehicle Selection Engine Campaign.

Generates 100+ NEW unique stress and boundary scenarios (no duplicate mission tuples).
"""

from dataclasses import dataclass
from typing import Any, List
import random

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode


@dataclass(slots=True)
class ValidationScenario:
    """
    Encapsulates a single scenario for the vehicle selection campaign.
    """
    case_id: str
    case_category: str  # DETERMINISTIC, BOUNDARY, AMBIGUOUS, CONFLICTING, INFEASIBLE, INVALID
    expected_family: str  # MULTIROTOR, FIXED_WING, VTOL, BOUNDARY, AMBIGUOUS, INFEASIBLE, INVALID
    expected_reasoning: str
    requirements: RequirementModel | dict[str, Any]
    hover_required: bool = False
    vertical_takeoff_required: bool = True
    runway_available: bool = False
    confined_operation: bool = False
    sweep_variable: str | None = None
    sweep_value: float | None = None


class StressScenarioGenerator:
    """
    Deterministic generator for 100+ unique stress scenarios.
    """

    def __init__(self, seed: int = 1001) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    def generate_stress_scenarios(self) -> List[ValidationScenario]:
        scenarios: List[ValidationScenario] = []

        # 1. Extreme Payload Stress Cases (15)
        for i in range(15):
            pay = 25.0 + (i * 3.0)  # 25 to 67 kg
            rng = 10.0 + (i * 1.5)  # 10 to 31 km
            case_id = f"CASE_STR_PAY_{i+1:03d}"
            req = RequirementModel(
                mission_type=MissionType.DELIVERY,
                payload_weight_kg=pay,
                target_flight_time_min=30.0 + i,
                target_range_km=rng,
                cruise_speed_kmh=60.0 + i,
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.RURAL,
            )
            if pay > 35.0:
                exp = "INFEASIBLE"
            elif rng >= 20.0:
                exp = "VTOL"
            else:
                exp = "MULTIROTOR"

            scenarios.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="DETERMINISTIC" if exp != "INFEASIBLE" else "INFEASIBLE",
                    expected_family=exp,
                    expected_reasoning=f"Stress payload testing at {pay:.1f} kg.",
                    requirements=req,
                    hover_required=True,
                    vertical_takeoff_required=True,
                )
            )

        # 2. Extreme Range Stress Cases (15)
        for i in range(15):
            rng = 220.0 + (i * 25.0)  # 220 to 570 km
            case_id = f"CASE_STR_RNG_{i+1:03d}"
            req = RequirementModel(
                mission_type=MissionType.SURVEY,
                payload_weight_kg=2.0,
                target_flight_time_min=180.0 + (i * 15),
                target_range_km=rng,
                cruise_speed_kmh=110.0 + i,
                takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY,
                environment=OperatingEnvironment.RURAL,
                optimization_priority=OptimizationPriority.MAXIMUM_RANGE,
            )
            exp = "FIXED_WING" if rng <= 450.0 else "INFEASIBLE"
            scenarios.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="DETERMINISTIC" if exp != "INFEASIBLE" else "INFEASIBLE",
                    expected_family=exp,
                    expected_reasoning=f"Stress range testing at {rng:.1f} km.",
                    requirements=req,
                    hover_required=False,
                    vertical_takeoff_required=False,
                    runway_available=True,
                )
            )

        # 3. High Altitude & Extreme Environment Stress Cases (20)
        envs = [
            OperatingEnvironment.MOUNTAIN,
            OperatingEnvironment.DESERT,
            OperatingEnvironment.COASTAL,
            OperatingEnvironment.MARINE,
            OperatingEnvironment.INDOOR,
        ]
        for i in range(20):
            case_id = f"CASE_STR_ENV_{i+1:03d}"
            env = envs[i % len(envs)]
            is_vtol_to = env in (OperatingEnvironment.INDOOR, OperatingEnvironment.URBAN, OperatingEnvironment.MARINE, OperatingEnvironment.MOUNTAIN, OperatingEnvironment.COASTAL)
            to_type = TakeoffType.VERTICAL if is_vtol_to else TakeoffType.RUNWAY
            ld_type = LandingType.VERTICAL if is_vtol_to else LandingType.RUNWAY
            rng = 15.0 + (i * 3)

            req = RequirementModel(
                mission_type=MissionType.RESEARCH,
                payload_weight_kg=1.5 + (i * 0.2),
                target_flight_time_min=35.0 + (i * 2),
                target_range_km=rng,
                cruise_speed_kmh=70.0 + i,
                takeoff_type=to_type,
                landing_type=ld_type,
                environment=env,
            )
            if env == OperatingEnvironment.INDOOR:
                exp = "MULTIROTOR"
            elif to_type == TakeoffType.VERTICAL:
                exp = "VTOL" if rng >= 20.0 else "MULTIROTOR"
            else:
                exp = "FIXED_WING"

            scenarios.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="DETERMINISTIC",
                    expected_family=exp,
                    expected_reasoning=f"Environmental stress test in {env.value}.",
                    requirements=req,
                    hover_required=(env == OperatingEnvironment.INDOOR),
                    vertical_takeoff_required=(to_type == TakeoffType.VERTICAL),
                    runway_available=(to_type == TakeoffType.RUNWAY),
                    confined_operation=(env in (OperatingEnvironment.INDOOR, OperatingEnvironment.URBAN)),
                )
            )

        # 4. Near-Tie & Transition Boundary Sweeps (25)
        for i in range(25):
            case_id = f"CASE_STR_BND_{i+1:03d}"
            rng = 25.0 + (i * 0.8)  # 25.0 to 44.2 km
            req = RequirementModel(
                mission_type=MissionType.SECURITY,
                payload_weight_kg=2.5,
                target_flight_time_min=45.0,
                target_range_km=rng,
                cruise_speed_kmh=75.0,
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.RURAL,
            )
            exp = "VTOL" if rng >= 25.0 else "MULTIROTOR"
            scenarios.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="BOUNDARY",
                    expected_family=exp,
                    expected_reasoning=f"Near-tie boundary sweep at range {rng:.1f} km.",
                    requirements=req,
                    hover_required=False,
                    vertical_takeoff_required=True,
                    sweep_variable="range_km",
                    sweep_value=rng,
                )
            )

        # 5. Conflicting Requirements & Edge Cases (25)
        for i in range(25):
            case_id = f"CASE_STR_CNF_{i+1:03d}"
            is_vertical = (i % 2 != 0)
            to_type = TakeoffType.VERTICAL if is_vertical else TakeoffType.HAND_LAUNCH
            ld_type = LandingType.VERTICAL if is_vertical else LandingType.PARACHUTE
            pay = 5.0 + i
            rng = 150.0 + (i * 5)

            req = RequirementModel(
                mission_type=MissionType.MILITARY,
                payload_weight_kg=pay,
                target_flight_time_min=90.0 + (i * 5),
                target_range_km=rng,
                cruise_speed_kmh=120.0,
                takeoff_type=to_type,
                landing_type=ld_type,
                environment=OperatingEnvironment.FOREST,
            )

            if pay > 20.0 and rng > 200.0:
                cat = "INFEASIBLE"
                exp = "INFEASIBLE"
            else:
                cat = "CONFLICTING"
                exp = "VTOL" if is_vertical else "FIXED_WING"

            scenarios.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category=cat,
                    expected_family=exp,
                    expected_reasoning="Military hand-launch / VTOL conflicting stress case.",
                    requirements=req,
                    hover_required=False,
                    vertical_takeoff_required=is_vertical,
                    runway_available=False,
                )
            )

        return scenarios
