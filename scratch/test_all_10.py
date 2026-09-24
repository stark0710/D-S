"""
Scratch script to probe all 10 missions through FixedWingDesignPipeline.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline.fixed_wing_pipeline import FixedWingDesignPipeline

missions = [
    {
        "id": "FW-01",
        "name": "Hobby Trainer",
        "mission_type": "HOBBY / TRAINER",
        "payload_weight_kg": 0.20,
        "target_range_km": 10.0,
        "target_flight_time_min": 15.0,
        "cruise_speed_kmh": 55.0,
    },
    {
        "id": "FW-02",
        "name": "Hobby Photography",
        "mission_type": "PHOTOGRAPHY",
        "payload_weight_kg": 0.30,
        "target_range_km": 20.0,
        "target_flight_time_min": 20.0,
        "cruise_speed_kmh": 65.0,
    },
    {
        "id": "FW-03",
        "name": "Hobby Long Endurance",
        "mission_type": "LONG ENDURANCE",
        "payload_weight_kg": 0.20,
        "target_range_km": 30.0,
        "target_flight_time_min": 45.0,
        "cruise_speed_kmh": 60.0,
    },
    {
        "id": "FW-04",
        "name": "Basic Survey",
        "mission_type": MissionType.SURVEY,
        "payload_weight_kg": 0.50,
        "target_range_km": 30.0,
        "target_flight_time_min": 30.0,
        "cruise_speed_kmh": 80.0,
    },
    {
        "id": "FW-05",
        "name": "Extended Survey",
        "mission_type": MissionType.SURVEY,
        "payload_weight_kg": 0.75,
        "target_range_km": 60.0,
        "target_flight_time_min": 60.0,
        "cruise_speed_kmh": 85.0,
    },
    {
        "id": "FW-06",
        "name": "Mapping UAV",
        "mission_type": MissionType.MAPPING,
        "payload_weight_kg": 1.00,
        "target_range_km": 50.0,
        "target_flight_time_min": 45.0,
        "cruise_speed_kmh": 90.0,
    },
    {
        "id": "FW-07",
        "name": "Heavy Payload UAV",
        "mission_type": "PAYLOAD / SURVEILLANCE",
        "payload_weight_kg": 1.50,
        "target_range_km": 40.0,
        "target_flight_time_min": 30.0,
        "cruise_speed_kmh": 75.0,
    },
    {
        "id": "FW-08",
        "name": "High Speed Survey",
        "mission_type": "HIGH SPEED SURVEY",
        "payload_weight_kg": 0.50,
        "target_range_km": 80.0,
        "target_flight_time_min": 40.0,
        "cruise_speed_kmh": 110.0,
    },
    {
        "id": "FW-09",
        "name": "Lightweight Student UAV",
        "mission_type": "EDUCATIONAL / STUDENT UAV",
        "payload_weight_kg": 0.25,
        "target_range_km": 15.0,
        "target_flight_time_min": 20.0,
        "cruise_speed_kmh": 60.0,
    },
    {
        "id": "FW-10",
        "name": "Long Range Surveillance",
        "mission_type": "LONG RANGE SURVEILLANCE",
        "payload_weight_kg": 0.75,
        "target_range_km": 100.0,
        "target_flight_time_min": 90.0,
        "cruise_speed_kmh": 80.0,
    },
]

pipeline = FixedWingDesignPipeline(raise_on_failure=False)

for m in missions:
    print(f"\n--- Testing {m['id']}: {m['name']} ---")
    req = RequirementModel(
        mission_type=m["mission_type"],
        payload_weight_kg=m["payload_weight_kg"],
        target_range_km=m["target_range_km"],
        target_flight_time_min=m["target_flight_time_min"],
        cruise_speed_kmh=m["cruise_speed_kmh"],
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )
    res = pipeline.execute(req)
    print(f"Result: success={res.success}, status={res.status}")
    if not res.success:
        print(f"Errors: {res.errors}")
        print(f"Warnings: {res.warnings}")
    else:
        spec = res.final_specification
        const = getattr(res.construction_result.selected_configuration, "name", "None") if res.construction_result else "None"
        mtow = spec.mass_properties.mtow_kg if spec and spec.mass_properties else "None"
        print(f"Success! MTOW={mtow:.3f} kg, Construction={const}")
