#!/usr/bin/env python3
"""
Test 4: Coastal Propagation Verification.
Executes a SURVEY case with environment=COASTAL, audits artifacts, and verifies:
- RequirementModel = COASTAL
- MissionProfile = MARINE
- EngineeringConstraints = MARINE
- No RURAL fallback in JSON or Markdown.
"""

import os
import sys
import json
import datetime

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from scripts.run_fixed_wing_pipeline import (
    execute_pipeline,
    audit_mass_accounting,
    save_json_artifact,
    save_markdown_report,
)

def main():
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.CATAPULT,
        landing_type=LandingType.BELLY_LANDING,
        environment=OperatingEnvironment.COASTAL,
    )
    
    print("Executing pipeline for SURVEY COASTAL...")
    res = execute_pipeline(req)
    mass_audit = audit_mass_accounting(res)
    
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = save_json_artifact(req, res, mass_audit, ts)
    md_path = save_markdown_report(req, res, mass_audit, ts)
    
    print(f"JSON artifact saved to: {json_path}")
    print(f"Markdown report saved to: {md_path}")
    
    # Verify in Python objects
    req_env = req.environment.value
    profile_env = res.mission_result.mission_profile.environment.value
    constraints_env = res.mission_result.constraints.operating_environment.value
    
    print("\n" + "="*50)
    print("OBJECT PROPAGATION CHECK:")
    print(f"RequirementModel.environment          : {req_env}")
    print(f"MissionProfile.environment            : {profile_env}")
    print(f"EngineeringConstraints.environment    : {constraints_env}")
    print("="*50)
    
    assert req_env == "COASTAL", f"Expected COASTAL, got {req_env}"
    assert profile_env == "Marine", f"Expected Marine, got {profile_env}"
    assert constraints_env == "Marine", f"Expected Marine, got {constraints_env}"
    
    # Inspect JSON artifact
    with open(json_path, "r") as f:
        data = json.load(f)
        
    json_req_env = data["requirements"]["environment"]
    json_prof_env = data["result"]["mission_result"]["mission_profile"]["environment"]
    json_const_env = data["result"]["mission_result"]["constraints"]["operating_environment"]
    
    print("\n" + "="*50)
    print("JSON ARTIFACT CHECK:")
    print(f"JSON user_requirements.environment   : {json_req_env}")
    print(f"JSON mission_profile.environment     : {json_prof_env}")
    print(f"JSON constraints.operating_env       : {json_const_env}")
    print("="*50)
    
    assert json_req_env == "COASTAL"
    assert json_prof_env == "Marine"
    assert json_const_env == "Marine"
    
    # Inspect Markdown report
    with open(md_path, "r") as f:
        md_text = f.read()
        
    print("\n" + "="*50)
    print("MARKDOWN REPORT CHECK:")
    has_coastal = "| **Environment** | `COASTAL` |" in md_text
    has_rural = "| **Environment** | `RURAL` |" in md_text
    print(f"Contains '| **Environment** | `COASTAL` |': {has_coastal}")
    print(f"Contains '| **Environment** | `RURAL` |': {has_rural}")
    print("="*50)
    
    assert has_coastal
    assert not has_rural
    
    print("\nALL COASTAL PROPAGATION CHECKS PASSED!")

if __name__ == "__main__":
    main()
