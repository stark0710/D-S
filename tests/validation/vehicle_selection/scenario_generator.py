"""
Deterministic Scenario Generator for Vehicle Selection Engine Validation.

Generates 600 test cases across MULTIROTOR, FIXED_WING, VTOL, BOUNDARY, CONFLICTING,
INFEASIBLE, and INVALID input categories.
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


class ScenarioGenerator:
    """
    Deterministic scenario generator for the 500+ case validation campaign.
    """

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    def generate_all_scenarios(self) -> List[ValidationScenario]:
        scenarios: List[ValidationScenario] = []
        
        # 1. Deterministic Multirotor cases (~150)
        scenarios.extend(self._generate_multirotor_cases(150))
        
        # 2. Deterministic Fixed-Wing cases (~150)
        scenarios.extend(self._generate_fixed_wing_cases(150))

        # 3. Deterministic VTOL cases (~150)
        scenarios.extend(self._generate_vtol_cases(150))

        # 4. Boundary / Ambiguous cases (~50)
        scenarios.extend(self._generate_boundary_cases(50))

        # 5. Conflicting mission cases (30)
        scenarios.extend(self._generate_conflicting_cases(30))

        # 6. Infeasible mission cases (20)
        scenarios.extend(self._generate_infeasible_cases(20))

        # 7. Invalid input cases (50)
        scenarios.extend(self._generate_invalid_cases(50))

        return scenarios

    def _generate_multirotor_cases(self, count: int) -> List[ValidationScenario]:
        cases: List[ValidationScenario] = []
        payloads = [0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 15.0]
        ranges = [1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 12.0, 14.0]
        endurances = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0]
        missions = [
            MissionType.INSPECTION,
            MissionType.SECURITY,
            MissionType.DISASTER_RESPONSE,
            MissionType.DELIVERY,
            MissionType.RESEARCH,
        ]
        environments = list(OperatingEnvironment)

        for i in range(count):
            case_id = f"CASE_MR_{i+1:03d}"
            payload = payloads[i % len(payloads)]
            rng_km = ranges[(i // 2) % len(ranges)]
            end_min = endurances[(i // 3) % len(endurances)]
            mission = missions[i % len(missions)]
            env = environments[i % len(environments)]
            
            req = RequirementModel(
                mission_type=mission,
                payload_weight_kg=payload,
                target_flight_time_min=end_min,
                target_range_km=rng_km,
                cruise_speed_kmh=40.0 + (i % 20),
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=env,
                optimization_priority=OptimizationPriority.BALANCED,
                design_mode=DesignMode.ENGINEERING_ADVISOR,
            )

            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="DETERMINISTIC",
                    expected_family="MULTIROTOR",
                    expected_reasoning="Short-range precision hover/inspection requirement.",
                    requirements=req,
                    hover_required=True,
                    vertical_takeoff_required=True,
                    runway_available=False,
                    confined_operation=(env == OperatingEnvironment.URBAN),
                )
            )
        return cases

    def _generate_fixed_wing_cases(self, count: int) -> List[ValidationScenario]:
        cases: List[ValidationScenario] = []
        payloads = [0.5, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0]
        ranges = [30.0, 45.0, 60.0, 80.0, 100.0, 120.0, 150.0, 200.0]
        endurances = [45.0, 60.0, 90.0, 120.0, 150.0, 180.0, 240.0]
        missions = [
            MissionType.SURVEY,
            MissionType.MAPPING,
            MissionType.AGRICULTURE,
            MissionType.MILITARY,
            MissionType.RESEARCH,
        ]
        takeoff_types = [TakeoffType.RUNWAY, TakeoffType.CATAPULT, TakeoffType.HAND_LAUNCH]

        for i in range(count):
            case_id = f"CASE_FW_{i+1:03d}"
            payload = payloads[i % len(payloads)]
            rng_km = ranges[(i // 2) % len(ranges)]
            end_min = endurances[(i // 3) % len(endurances)]
            mission = missions[i % len(missions)]
            to_type = takeoff_types[i % len(takeoff_types)]
            landing_type = LandingType.PARACHUTE if to_type == TakeoffType.CATAPULT else LandingType.RUNWAY

            req = RequirementModel(
                mission_type=mission,
                payload_weight_kg=payload,
                target_flight_time_min=end_min,
                target_range_km=rng_km,
                cruise_speed_kmh=80.0 + (i % 40),
                takeoff_type=to_type,
                landing_type=landing_type,
                environment=OperatingEnvironment.RURAL,
                optimization_priority=OptimizationPriority.MAXIMUM_RANGE,
                design_mode=DesignMode.ENGINEERING_ADVISOR,
            )

            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="DETERMINISTIC",
                    expected_family="FIXED_WING",
                    expected_reasoning="Long-range, high-efficiency wing-borne cruise with non-vertical takeoff.",
                    requirements=req,
                    hover_required=False,
                    vertical_takeoff_required=False,
                    runway_available=(to_type == TakeoffType.RUNWAY),
                    confined_operation=False,
                )
            )
        return cases

    def _generate_vtol_cases(self, count: int) -> List[ValidationScenario]:
        cases: List[ValidationScenario] = []
        payloads = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0]
        ranges = [30.0, 45.0, 60.0, 80.0, 100.0, 120.0, 150.0]
        endurances = [45.0, 60.0, 90.0, 120.0, 150.0, 180.0]
        missions = [
            MissionType.DISASTER_RESPONSE,
            MissionType.DELIVERY,
            MissionType.SECURITY,
            MissionType.MAPPING,
            MissionType.SURVEY,
        ]

        for i in range(count):
            case_id = f"CASE_VTOL_{i+1:03d}"
            payload = payloads[i % len(payloads)]
            rng_km = ranges[(i // 2) % len(ranges)]
            end_min = endurances[(i // 3) % len(endurances)]
            mission = missions[i % len(missions)]

            req = RequirementModel(
                mission_type=mission,
                payload_weight_kg=payload,
                target_flight_time_min=end_min,
                target_range_km=rng_km,
                cruise_speed_kmh=85.0 + (i % 35),
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.FOREST if i % 2 == 0 else OperatingEnvironment.MOUNTAIN,
                optimization_priority=OptimizationPriority.BALANCED,
                design_mode=DesignMode.ENGINEERING_ADVISOR,
            )

            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="DETERMINISTIC",
                    expected_family="VTOL",
                    expected_reasoning="Combines mandatory vertical takeoff with long range (> 30 km).",
                    requirements=req,
                    hover_required=False,
                    vertical_takeoff_required=True,
                    runway_available=False,
                    confined_operation=True,
                )
            )
        return cases

    def _generate_boundary_cases(self, count: int) -> List[ValidationScenario]:
        cases: List[ValidationScenario] = []

        # Range sweep from 5 km to 45 km with TakeoffType.VERTICAL
        sweep_ranges = [5.0, 10.0, 15.0, 20.0, 25.0, 28.0, 30.0, 32.0, 35.0, 40.0, 45.0]
        for idx, r in enumerate(sweep_ranges):
            case_id = f"CASE_BND_RNG_{idx+1:02d}"
            req = RequirementModel(
                mission_type=MissionType.SURVEY,
                payload_weight_kg=2.0,
                target_flight_time_min=45.0,
                target_range_km=r,
                cruise_speed_kmh=75.0,
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.RURAL,
                optimization_priority=OptimizationPriority.BALANCED,
            )
            exp = "MULTIROTOR" if r < 15.0 else ("VTOL" if r >= 30.0 else "BOUNDARY")
            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="BOUNDARY" if exp == "BOUNDARY" else "DETERMINISTIC",
                    expected_family=exp,
                    expected_reasoning=f"Range sweep transition point at {r} km.",
                    requirements=req,
                    sweep_variable="range_km",
                    sweep_value=r,
                )
            )

        # Payload sweep from 1 kg to 15 kg for Multirotors
        sweep_payloads = [1.0, 3.0, 5.0, 7.0, 9.0, 10.0, 11.0, 13.0, 15.0]
        for idx, p in enumerate(sweep_payloads):
            case_id = f"CASE_BND_PAY_{idx+1:02d}"
            req = RequirementModel(
                mission_type=MissionType.DELIVERY,
                payload_weight_kg=p,
                target_flight_time_min=25.0,
                target_range_km=8.0,
                cruise_speed_kmh=50.0,
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.URBAN,
            )
            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="BOUNDARY",
                    expected_family="MULTIROTOR",
                    expected_reasoning=f"Multirotor payload capacity transition at {p} kg.",
                    requirements=req,
                    sweep_variable="payload_kg",
                    sweep_value=p,
                )
            )

        # Remaining cases to reach 50 boundary cases
        needed = count - len(cases)
        for i in range(needed):
            case_id = f"CASE_BND_AMB_{i+1:02d}"
            req = RequirementModel(
                mission_type=MissionType.INSPECTION,
                payload_weight_kg=1.5,
                target_flight_time_min=30.0 + i,
                target_range_km=18.0 + (i * 0.5),
                cruise_speed_kmh=60.0,
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.URBAN,
            )
            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="AMBIGUOUS",
                    expected_family="AMBIGUOUS",
                    expected_reasoning="Mid-range (18-25 km) requirement with vertical takeoff.",
                    requirements=req,
                )
            )

        return cases

    def _generate_conflicting_cases(self, count: int) -> List[ValidationScenario]:
        cases: List[ValidationScenario] = []
        conflicts = [
            ("Long range (100km) + Hover Mandatory + Vertical Takeoff", 100.0, 90.0, 2.0, TakeoffType.VERTICAL, True),
            ("Very long endurance (180m) + Heavy payload (15kg) + Urban confined", 30.0, 180.0, 15.0, TakeoffType.VERTICAL, True),
            ("High speed (150km/h) + Sustained hover + Quadcopter preference", 20.0, 30.0, 1.0, TakeoffType.VERTICAL, True),
            ("Long range (120km) + No runway + Conventional takeoff request", 120.0, 120.0, 3.0, TakeoffType.RUNWAY, False),
            ("Small payload (0.1kg) + Short range (2km) + Mandatory Catapult", 2.0, 15.0, 0.1, TakeoffType.CATAPULT, False),
        ]

        for i in range(count):
            case_id = f"CASE_CNF_{i+1:03d}"
            desc, rng_km, end_min, pay_kg, to_type, hover = conflicts[i % len(conflicts)]
            req = RequirementModel(
                mission_type=MissionType.SECURITY,
                payload_weight_kg=pay_kg,
                target_flight_time_min=end_min,
                target_range_km=rng_km,
                cruise_speed_kmh=90.0,
                takeoff_type=to_type,
                landing_type=LandingType.VERTICAL if to_type == TakeoffType.VERTICAL else LandingType.RUNWAY,
                environment=OperatingEnvironment.URBAN if hover else OperatingEnvironment.RURAL,
            )
            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="CONFLICTING",
                    expected_family="AMBIGUOUS",
                    expected_reasoning=f"Conflicting requirements: {desc}",
                    requirements=req,
                    hover_required=hover,
                    vertical_takeoff_required=(to_type == TakeoffType.VERTICAL),
                )
            )
        return cases

    def _generate_infeasible_cases(self, count: int) -> List[ValidationScenario]:
        cases: List[ValidationScenario] = []
        infeasible_specs = [
            ("Extreme payload (100kg)", 100.0, 10.0, 60.0, 100.0),
            ("Extreme range (2000km)", 2.0, 2000.0, 300.0, 150.0),
            ("Extreme endurance (1000min)", 1.0, 50.0, 1000.0, 80.0),
            ("Extreme payload + Extreme range (50kg, 500km)", 50.0, 500.0, 240.0, 200.0),
        ]

        for i in range(count):
            case_id = f"CASE_INF_{i+1:03d}"
            desc, pay, rng_km, end_min, spd = infeasible_specs[i % len(infeasible_specs)]
            req = RequirementModel(
                mission_type=MissionType.DELIVERY,
                payload_weight_kg=pay,
                target_flight_time_min=end_min,
                target_range_km=rng_km,
                cruise_speed_kmh=spd,
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.RURAL,
            )
            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="INFEASIBLE",
                    expected_family="INFEASIBLE",
                    expected_reasoning=f"Infeasible mission: {desc}",
                    requirements=req,
                )
            )
        return cases

    def _generate_invalid_cases(self, count: int) -> List[ValidationScenario]:
        cases: List[ValidationScenario] = []
        invalid_dicts = [
            ("Negative payload (-5.0 kg)", {"mission_type": MissionType.SURVEY, "payload_weight_kg": -5.0, "target_flight_time_min": 30.0, "target_range_km": 10.0, "cruise_speed_kmh": 60.0}),
            ("Zero payload (0.0 kg)", {"mission_type": MissionType.SURVEY, "payload_weight_kg": 0.0, "target_flight_time_min": 30.0, "target_range_km": 10.0, "cruise_speed_kmh": 60.0}),
            ("Negative range (-10.0 km)", {"mission_type": MissionType.SURVEY, "payload_weight_kg": 2.0, "target_flight_time_min": 30.0, "target_range_km": -10.0, "cruise_speed_kmh": 60.0}),
            ("Zero flight time (0.0 min)", {"mission_type": MissionType.SURVEY, "payload_weight_kg": 2.0, "target_flight_time_min": 0.0, "target_range_km": 10.0, "cruise_speed_kmh": 60.0}),
            ("Negative cruise speed (-40.0 km/h)", {"mission_type": MissionType.SURVEY, "payload_weight_kg": 2.0, "target_flight_time_min": 30.0, "target_range_km": 10.0, "cruise_speed_kmh": -40.0}),
            ("Negative budget (-500.0 USD)", {"mission_type": MissionType.SURVEY, "payload_weight_kg": 2.0, "target_flight_time_min": 30.0, "target_range_km": 10.0, "cruise_speed_kmh": 60.0, "budget": -500.0}),
            ("Negative MTOW (-10.0 kg)", {"mission_type": MissionType.SURVEY, "payload_weight_kg": 2.0, "target_flight_time_min": 30.0, "target_range_km": 10.0, "cruise_speed_kmh": 60.0, "maximum_takeoff_weight_kg": -10.0}),
        ]

        for i in range(count):
            case_id = f"CASE_INV_{i+1:03d}"
            desc, req_dict = invalid_dicts[i % len(invalid_dicts)]
            
            try:
                req = RequirementModel(
                    mission_type=req_dict.get("mission_type", MissionType.SURVEY),
                    payload_weight_kg=req_dict.get("payload_weight_kg", 2.0),
                    target_flight_time_min=req_dict.get("target_flight_time_min", 30.0),
                    target_range_km=req_dict.get("target_range_km", 10.0),
                    cruise_speed_kmh=req_dict.get("cruise_speed_kmh", 60.0),
                    budget=req_dict.get("budget"),
                    maximum_takeoff_weight_kg=req_dict.get("maximum_takeoff_weight_kg"),
                )
            except Exception:
                req = req_dict

            cases.append(
                ValidationScenario(
                    case_id=case_id,
                    case_category="INVALID",
                    expected_family="INVALID",
                    expected_reasoning=f"Invalid requirement parameters: {desc}",
                    requirements=req,
                )
            )
        return cases
