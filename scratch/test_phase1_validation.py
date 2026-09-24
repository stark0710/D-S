#!/usr/bin/env python3
"""
Phase 1 Validation Script.
Executes TEST 1, TEST 2, TEST 3, TEST 4 and Regression Baselines:
- TEST 1: RESEARCH (0.8 kg, MOUNTAINOUS)
- TEST 2: TRAINING (0.2 kg, RURAL)
- TEST 3: DELIVERY (1.0 kg, COASTAL)
- TEST 4: COASTAL PROPAGATION INSPECTION
- REGRESSION 1: SURVEY (0.5 kg, RURAL)
- REGRESSION 2: SURVEY (1.0 kg, RURAL)
- REGRESSION 3: AGRICULTURE (2.0 kg, RURAL)
"""

import sys
import os
import json

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

def run_case(name: str, req: RequirementModel):
    print(f"\n{'='*60}\nRUNNING: {name}\n{'='*60}")
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    res = pipeline.execute(req)
    
    print(f"Status: {res.status}")
    print(f"Success: {res.success}")
    print(f"Converged: {res.converged}")
    print(f"Iterations: {res.iterations}")
    
    # Environment propagation
    if res.mission_result:
        mp_env = getattr(res.mission_result.mission_profile, 'environment', None)
        mc_env = getattr(res.mission_result.constraints, 'operating_environment', None)
        print(f"Req Env: {req.environment.value} | Profile Env: {mp_env} | Constraints Env: {mc_env}")
    
    # Payload details
    if res.payload_result:
        pr = res.payload_result
        print(f"Selected Payloads: {getattr(pr, 'selected_payloads', None)}")
        print(f"Requested Payload Mass: {getattr(pr, 'requested_payload_mass_kg', None)} kg")
        print(f"Installed Payload Mass: {getattr(pr, 'installed_payload_mass_kg', None)} kg")
    else:
        print("Payload Result: None")
        
    if res.errors:
        print(f"Errors: {res.errors}")
    if res.warnings:
        print(f"Warnings: {res.warnings[:3]}")
        
    return res

def main():
    results = {}
    
    # TEST 1: RESEARCH
    req_research = RequirementModel(
        mission_type=MissionType.RESEARCH,
        payload_weight_kg=0.8,
        target_flight_time_min=40.0,
        target_range_km=60.0,
        cruise_speed_kmh=90.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.MOUNTAIN,
    )
    results["RESEARCH"] = run_case("TEST 1: RESEARCH (0.8 kg)", req_research)
    
    # TEST 2: TRAINING
    req_training = RequirementModel(
        mission_type=MissionType.TRAINING,
        payload_weight_kg=0.2,
        target_flight_time_min=15.0,
        target_range_km=15.0,
        cruise_speed_kmh=60.0,
        takeoff_type=TakeoffType.HAND_LAUNCH,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
    )
    results["TRAINING"] = run_case("TEST 2: TRAINING (0.2 kg)", req_training)
    
    # TEST 3: DELIVERY
    req_delivery = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=1.0,
        target_flight_time_min=45.0,
        target_range_km=80.0,
        cruise_speed_kmh=90.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.COASTAL,
    )
    results["DELIVERY_1KG"] = run_case("TEST 3: DELIVERY (1.0 kg, COASTAL)", req_delivery)
    
    # REGRESSION 1: SURVEY 0.5 kg
    req_survey_05 = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
    )
    results["SURVEY_05"] = run_case("REGRESSION 1: SURVEY (0.5 kg)", req_survey_05)
    
    # REGRESSION 2: SURVEY 1.0 kg
    req_survey_10 = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=50.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
    )
    results["SURVEY_10"] = run_case("REGRESSION 2: SURVEY (1.0 kg)", req_survey_10)
    
    # REGRESSION 3: AGRICULTURE 2.0 kg
    req_agri = RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=25.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.RURAL,
    )
    results["AGRICULTURE"] = run_case("REGRESSION 3: AGRICULTURE (2.0 kg)", req_agri)

if __name__ == "__main__":
    main()
