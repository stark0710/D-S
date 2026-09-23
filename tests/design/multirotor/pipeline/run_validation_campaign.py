import os
import sys

# Ensure backend and tests are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.multirotor.pipeline.multirotor_design_pipeline import MultirotorDesignPipeline
from backend.design.multirotor.pipeline.pipeline_result import PipelineStatus


def run_campaign():
    pipeline = MultirotorDesignPipeline()
    cases = []
    
    # 1. Small Photography Quad
    cases.append((
        "Small photography quad",
        RequirementModel(
            mission_type=MissionType.MAPPING,
            payload_weight_kg=0.3,
            target_flight_time_min=20.0,
            target_range_km=5.0,
            cruise_speed_kmh=30.0,
            environment=OperatingEnvironment.URBAN,
            metadata={"payload_dimensions_m": (0.05, 0.05, 0.04), "redundancy_required": False}
        )
    ))
    
    # 2. Mapping Quad
    cases.append((
        "Mapping quad",
        RequirementModel(
            mission_type=MissionType.MAPPING,
            payload_weight_kg=1.0,
            target_flight_time_min=25.0,
            target_range_km=15.0,
            cruise_speed_kmh=40.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.12, 0.10, 0.08), "redundancy_required": False}
        )
    ))
    
    # 3. Inspection Quad
    cases.append((
        "Inspection quad",
        RequirementModel(
            mission_type=MissionType.INSPECTION,
            payload_weight_kg=0.8,
            target_flight_time_min=20.0,
            target_range_km=8.0,
            cruise_speed_kmh=35.0,
            environment=OperatingEnvironment.FOREST,
            metadata={"payload_dimensions_m": (0.10, 0.08, 0.06), "redundancy_required": False}
        )
    ))
    
    # 4. Survey Quad
    cases.append((
        "Survey quad",
        RequirementModel(
            mission_type=MissionType.SURVEY,
            payload_weight_kg=1.2,
            target_flight_time_min=30.0,
            target_range_km=20.0,
            cruise_speed_kmh=40.0,
            environment=OperatingEnvironment.MOUNTAIN,
            metadata={"payload_dimensions_m": (0.15, 0.10, 0.08), "redundancy_required": False}
        )
    ))
    
    # 5. Security Quad
    cases.append((
        "Security quad",
        RequirementModel(
            mission_type=MissionType.SECURITY,
            payload_weight_kg=0.5,
            target_flight_time_min=30.0,
            target_range_km=12.0,
            cruise_speed_kmh=45.0,
            environment=OperatingEnvironment.URBAN,
            metadata={"payload_dimensions_m": (0.08, 0.08, 0.06), "redundancy_required": False}
        )
    ))
    
    # 6. Long-Endurance Quad
    cases.append((
        "Long-endurance quad",
        RequirementModel(
            mission_type=MissionType.RESEARCH,
            payload_weight_kg=0.4,
            target_flight_time_min=40.0,
            target_range_km=30.0,
            cruise_speed_kmh=30.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.06, 0.06, 0.05), "redundancy_required": False}
        )
    ))
    
    # 7. Heavy-Payload Quad
    cases.append((
        "Heavy-payload quad",
        RequirementModel(
            mission_type=MissionType.DELIVERY,
            payload_weight_kg=4.0,
            target_flight_time_min=15.0,
            target_range_km=10.0,
            cruise_speed_kmh=40.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.25, 0.20, 0.15), "redundancy_required": False, "maximum_frame_size_m": 1.5}
        )
    ))
    
    # 8. Cargo Quad
    cases.append((
        "Cargo quad",
        RequirementModel(
            mission_type=MissionType.DELIVERY,
            payload_weight_kg=3.0,
            target_flight_time_min=20.0,
            target_range_km=15.0,
            cruise_speed_kmh=38.0,
            environment=OperatingEnvironment.URBAN,
            metadata={"payload_dimensions_m": (0.22, 0.18, 0.12), "redundancy_required": False, "maximum_frame_size_m": 1.4}
        )
    ))
    
    # 9. Hexacopter
    cases.append((
        "Hexacopter",
        RequirementModel(
            mission_type=MissionType.MAPPING,
            payload_weight_kg=2.0,
            target_flight_time_min=25.0,
            target_range_km=15.0,
            cruise_speed_kmh=40.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.18, 0.15, 0.10), "redundancy_required": True, "maximum_frame_size_m": 1.0}
        )
    ))
    
    # 10. Octocopter
    cases.append((
        "Octocopter",
        RequirementModel(
            mission_type=MissionType.DELIVERY,
            payload_weight_kg=5.0,
            target_flight_time_min=18.0,
            target_range_km=12.0,
            cruise_speed_kmh=35.0,
            environment=OperatingEnvironment.URBAN,
            metadata={"payload_dimensions_m": (0.30, 0.25, 0.18), "redundancy_required": True, "maximum_frame_size_m": 1.5}
        )
    ))
    
    # 11. Coaxial Configuration
    cases.append((
        "Coaxial configuration",
        RequirementModel(
            mission_type=MissionType.MILITARY,
            payload_weight_kg=6.0,
            target_flight_time_min=20.0,
            target_range_km=20.0,
            cruise_speed_kmh=45.0,
            environment=OperatingEnvironment.MOUNTAIN,
            metadata={"payload_dimensions_m": (0.35, 0.25, 0.20), "redundancy_required": True, "multirotor_mission": "Heavy Lift", "maximum_frame_size_m": 1.6}
        )
    ))
    
    # 12. Lightweight Case
    cases.append((
        "Lightweight case",
        RequirementModel(
            mission_type=MissionType.RESEARCH,
            payload_weight_kg=0.1,
            target_flight_time_min=15.0,
            target_range_km=2.0,
            cruise_speed_kmh=25.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.04, 0.04, 0.03), "redundancy_required": False}
        )
    ))
    
    # 13. High-Payload Case
    cases.append((
        "High-payload case",
        RequirementModel(
            mission_type=MissionType.DELIVERY,
            payload_weight_kg=4.5,
            target_flight_time_min=20.0,
            target_range_km=10.0,
            cruise_speed_kmh=40.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.28, 0.22, 0.16), "redundancy_required": False, "maximum_frame_size_m": 1.5}
        )
    ))
    
    # 14. Long-Endurance Case
    cases.append((
        "Long-endurance case",
        RequirementModel(
            mission_type=MissionType.RESEARCH,
            payload_weight_kg=0.2,
            target_flight_time_min=45.0,
            target_range_km=25.0,
            cruise_speed_kmh=30.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.05, 0.05, 0.04), "redundancy_required": False}
        )
    ))
    
    # 15. Near-Limit Case
    cases.append((
        "Near-limit case",
        RequirementModel(
            mission_type=MissionType.DELIVERY,
            payload_weight_kg=6.5,
            target_flight_time_min=15.0,
            target_range_km=15.0,
            cruise_speed_kmh=40.0,
            environment=OperatingEnvironment.MOUNTAIN,
            metadata={"payload_dimensions_m": (0.35, 0.30, 0.20), "redundancy_required": True, "maximum_frame_size_m": 1.6}
        )
    ))
    
    # 16. Invalid Requirements
    cases.append((
        "Invalid requirements",
        RequirementModel(
            mission_type=MissionType.MAPPING,
            payload_weight_kg=-0.5,
            target_flight_time_min=0.0,
            target_range_km=-10.0,
            cruise_speed_kmh=0.0,
            environment=OperatingEnvironment.RURAL
        )
    ))
    
    # 17. Database Limitation (No frames match size)
    cases.append((
        "Database limitation",
        RequirementModel(
            mission_type=MissionType.MAPPING,
            payload_weight_kg=1.0,
            target_flight_time_min=20.0,
            target_range_km=10.0,
            cruise_speed_kmh=30.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.1, 0.1, 0.08), "maximum_frame_size_m": 0.15}  # Too small for any frame
        )
    ))
    
    # 18. Incompatible Frame Case (Large payload doesn't fit bay size)
    cases.append((
        "Incompatible frame case",
        RequirementModel(
            mission_type=MissionType.MAPPING,
            payload_weight_kg=0.5,
            target_flight_time_min=20.0,
            target_range_km=10.0,
            cruise_speed_kmh=30.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"payload_dimensions_m": (0.8, 0.8, 0.8), "maximum_frame_size_m": 0.6}  # Payload size exceeds wheelbase limit
        )
    ))
    
    # 19. Propulsion Infeasible Case (Extreme payload mass)
    cases.append((
        "Propulsion infeasible case",
        RequirementModel(
            mission_type=MissionType.DELIVERY,
            payload_weight_kg=50.0,  # Far too heavy for catalog parts
            target_flight_time_min=20.0,
            target_range_km=10.0,
            cruise_speed_kmh=30.0,
            environment=OperatingEnvironment.RURAL
        )
    ))
    
    # 20. Verification Failure Case (Exceeds maximum MTOW threshold for strategy)
    cases.append((
        "Verification failure case",
        RequirementModel(
            mission_type=MissionType.MAPPING,
            payload_weight_kg=20.0,  # Sizing succeeded but fails MTOW rule limit
            target_flight_time_min=20.0,
            target_range_km=10.0,
            cruise_speed_kmh=30.0,
            environment=OperatingEnvironment.RURAL,
            metadata={"maximum_frame_size_m": 1.6, "payload_dimensions_m": (0.2, 0.2, 0.15)}
        )
    ))

    results = []
    success_count = 0
    
    print("Executing 20-case validation campaign...")
    for idx, (name, req) in enumerate(cases, 1):
        res = pipeline.execute(req)
        status_name = res.status.name if hasattr(res.status, "name") else str(res.status)
        results.append({
            "id": idx,
            "name": name,
            "success": res.success,
            "status": status_name,
            "iterations": res.iterations,
            "mtow_kg": res.final_specification.mtow_kg if res.success else 0.0,
            "errors": "; ".join(res.errors) if res.errors else "None"
        })
        if res.success:
            success_count += 1
        print(f"[{idx}/20] {name}: Success={res.success}, Status={status_name}")

    # Generate Campaign Report
    report_content = f"""# Multirotor Pipeline 20-Case Validation Campaign Report

This report summarizes the design synthesis and verification campaign of the **Sprint 43 Multirotor V1 Design Pipeline** over **20 representative test cases**.

## Summary
*   **Total Test Cases**: 20
*   **Successful Designs**: {success_count}/20
*   **Validation Status**: Verified and Sized

## Campaign Ledger
| Case ID | Case Description | Success | Status Code | Iterations | Sized MTOW (kg) | Diagnostics / Errors |
|---|---|---|---|---|---|---|
"""
    for r in results:
        report_content += f"| {r['id']} | {r['name']} | {'✓ YES' if r['success'] else '✗ NO'} | {r['status']} | {r['iterations']} | {r['mtow_kg']:.2f} | {r['errors']} |\n"

    os.makedirs("reports", exist_ok=True)
    with open("reports/multirotor_pipeline_validation_campaign.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Validation campaign complete. Report written to reports/multirotor_pipeline_validation_campaign.md. Passed {success_count}/20 successful sizing configurations.")


if __name__ == "__main__":
    run_campaign()
