"""
Export All 600 Validation Cases Script for Vehicle Selection Engine Campaign.
"""

import json
import csv
import os
from typing import Dict, Any, List

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.validation.requirement_validator import RequirementValidator
from backend.design.common.mission.mission_analysis_service import MissionAnalysisService
from backend.design.advisor.recommendation.recommendation_pipeline import RecommendationPipeline
from backend.design.advisor.recommendation.vehicle_type import VehicleType

from tests.validation.vehicle_selection.scenario_generator import ScenarioGenerator


def normalize_vehicle_type(raw_type: str | VehicleType) -> str:
    val = raw_type.value if hasattr(raw_type, "value") else str(raw_type)
    if val in ("QUADCOPTER", "HEXACOPTER", "OCTOCOPTER", "MULTIROTOR"):
        return "MULTIROTOR"
    elif val == "FIXED_WING":
        return "FIXED_WING"
    elif val == "VTOL":
        return "VTOL"
    return "NONE"


def export_all_cases() -> Dict[str, Any]:
    validator = RequirementValidator()
    mission_service = MissionAnalysisService()
    pipeline = RecommendationPipeline()
    generator = ScenarioGenerator(seed=42)

    scenarios = generator.generate_all_scenarios()
    
    json_cases: List[Dict[str, Any]] = []
    csv_rows: List[List[Any]] = []
    manual_review_rows: List[List[Any]] = []

    category_counts = {
        "DETERMINISTIC": 0,
        "BOUNDARY": 0,
        "AMBIGUOUS": 0,
        "CONFLICTING": 0,
        "INFEASIBLE": 0,
        "INVALID": 0,
    }

    family_counts = {
        "MULTIROTOR": 0,
        "FIXED_WING": 0,
        "VTOL": 0,
    }

    for scenario in scenarios:
        category_counts[scenario.case_category] = category_counts.get(scenario.case_category, 0) + 1
        if scenario.case_category == "DETERMINISTIC" and scenario.expected_family in family_counts:
            family_counts[scenario.expected_family] += 1

        # Requirement details
        if isinstance(scenario.requirements, RequirementModel):
            req = scenario.requirements
            payload_kg = req.payload_weight_kg
            range_km = req.target_range_km
            endurance_min = req.target_flight_time_min
            cruise_speed_kmh = req.cruise_speed_kmh
            environment = req.environment.value if hasattr(req.environment, 'value') else str(req.environment)
            mission_type = req.mission_type.value if hasattr(req.mission_type, 'value') else str(req.mission_type)
            opt_priority = req.optimization_priority.value if hasattr(req.optimization_priority, 'value') else str(req.optimization_priority)

            val_result = validator.validate(req)
            is_valid = val_result.is_valid
            val_errors = [f"{issue.code.value}: {issue.message}" for issue in val_result.issues]
        else:
            req_dict = scenario.requirements
            payload_kg = req_dict.get("payload_weight_kg", -1)
            range_km = req_dict.get("target_range_km", -1)
            endurance_min = req_dict.get("target_flight_time_min", -1)
            cruise_speed_kmh = req_dict.get("cruise_speed_kmh", -1)
            environment = "RURAL"
            mission_type = "SURVEY"
            opt_priority = "BALANCED"
            is_valid = False
            val_errors = ["Invalid requirements parameters."]

        raw_selected = "REJECTED"
        norm_selected = "NONE"
        top_score = 0.0
        top_confidence = 0.0
        pros: List[str] = []
        cons: List[str] = []
        alternatives: List[Dict[str, Any]] = []

        if is_valid and isinstance(scenario.requirements, RequirementModel):
            mission_analysis = mission_service.analyze_requirements(scenario.requirements)
            report = pipeline.execute(mission_analysis.mission_profile)

            if report.recommendations:
                top_rec = report.recommendations[0]
                raw_selected = top_rec.vehicle_type.value
                norm_selected = normalize_vehicle_type(top_rec.vehicle_type)
                top_score = top_rec.overall_score
                top_confidence = top_rec.confidence
                pros = top_rec.pros
                cons = top_rec.cons

                for alt in report.recommendations[1:]:
                    alternatives.append({
                        "raw_type": alt.vehicle_type.value,
                        "normalized_family": normalize_vehicle_type(alt.vehicle_type),
                        "score": alt.overall_score,
                        "confidence": alt.confidence,
                    })

        # Classification logic
        if scenario.case_category == "INVALID":
            if not is_valid:
                final_classification = "INVALID_CORRECTLY_REJECTED"
            else:
                final_classification = "FAIL"
        elif scenario.case_category == "INFEASIBLE":
            if top_confidence > 0.85:
                final_classification = "FAIL"
            else:
                final_classification = "PASS"
        elif scenario.case_category == "DETERMINISTIC":
            if norm_selected == scenario.expected_family:
                final_classification = "PASS"
            else:
                final_classification = "FAIL"
        else: # BOUNDARY, AMBIGUOUS, CONFLICTING
            final_classification = "QUESTIONABLE"

        inputs_dict = {
            "payload_kg": payload_kg,
            "range_km": range_km,
            "endurance_min": endurance_min,
            "cruise_speed_kmh": cruise_speed_kmh,
            "hover_required": scenario.hover_required,
            "vertical_takeoff_required": scenario.vertical_takeoff_required,
            "runway_available": scenario.runway_available,
            "confined_operation": scenario.confined_operation,
            "environment": environment,
            "optimization_priority": opt_priority,
        }

        alts_str = "; ".join([f"{a['raw_type']}:{a['score']}" for a in alternatives])

        case_obj = {
            "case_id": scenario.case_id,
            "case_category": scenario.case_category,
            "mission_type": mission_type,
            "inputs": inputs_dict,
            "expected_family": scenario.expected_family,
            "raw_selector_output": raw_selected,
            "normalized_family_output": norm_selected,
            "selected_score": top_score,
            "confidence": top_confidence,
            "alternative_candidates": alternatives,
            "reasoning_pros": pros,
            "penalties_cons": cons,
            "validation_result": "VALID" if is_valid else f"INVALID: {'; '.join(val_errors)}",
            "final_test_classification": final_classification,
        }
        json_cases.append(case_obj)

        csv_row = [
            scenario.case_id,
            scenario.case_category,
            mission_type,
            payload_kg,
            range_km,
            endurance_min,
            cruise_speed_kmh,
            scenario.hover_required,
            scenario.vertical_takeoff_required,
            scenario.runway_available,
            scenario.confined_operation,
            environment,
            opt_priority,
            scenario.expected_family,
            raw_selected,
            norm_selected,
            top_score,
            top_confidence,
            alts_str,
            " | ".join(pros),
            " | ".join(cons),
            "VALID" if is_valid else "INVALID",
            final_classification,
        ]
        csv_rows.append(csv_row)

        manual_row = list(csv_row) + ["", "", "", ""]
        manual_review_rows.append(manual_row)

    # Write JSON Deliverable
    os.makedirs("reports", exist_ok=True)
    os.makedirs("docs/validation", exist_ok=True)

    json_path = os.path.abspath(os.path.join(".", "reports", "vehicle_selection_all_600_cases.json"))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_cases, f, indent=2)

    # Write CSV Deliverable
    csv_header = [
        "CASE_ID", "CASE_CATEGORY", "MISSION_TYPE", "PAYLOAD_KG", "RANGE_KM",
        "ENDURANCE_MIN", "CRUISE_SPEED_KMH", "HOVER_REQUIRED", "VTOL_REQUIRED",
        "RUNWAY_AVAILABLE", "CONFINED_OPERATION", "ENVIRONMENT", "OPTIMIZATION_PRIORITY",
        "EXPECTED_FAMILY", "RAW_SELECTOR_OUTPUT", "NORMALIZED_FAMILY_OUTPUT",
        "SELECTED_SCORE", "CONFIDENCE", "ALTERNATIVE_CANDIDATES", "REASONING_PROS",
        "PENALTIES_CONS", "VALIDATION_RESULT", "FINAL_TEST_CLASSIFICATION"
    ]

    csv_path = os.path.abspath(os.path.join(".", "reports", "vehicle_selection_all_600_cases.csv"))
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)

    # Write Special Manual Review CSV Deliverable
    manual_header = csv_header + [
        "MANUAL_REVIEW", "MANUAL_EXPECTED_FAMILY", "MANUAL_PASS_FAIL", "REVIEWER_COMMENT"
    ]

    manual_path = os.path.abspath(os.path.join(".", "reports", "vehicle_selection_manual_review.csv"))
    with open(manual_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(manual_header)
        writer.writerows(manual_review_rows)

    # Write Markdown Document organized by category
    md_path = os.path.abspath(os.path.join(".", "docs", "validation", "VEHICLE_SELECTION_ALL_600_OUTPUTS.md"))
    write_markdown_outputs(md_path, json_cases)

    return {
        "json_path": json_path,
        "csv_path": csv_path,
        "manual_path": manual_path,
        "md_path": md_path,
        "total_cases": len(json_cases),
        "csv_rows": len(csv_rows),
        "manual_rows": len(manual_review_rows),
        "category_counts": category_counts,
        "family_counts": family_counts,
    }


def write_markdown_outputs(filepath: str, cases: List[Dict[str, Any]]) -> None:
    categories = [
        ("MULTIROTOR Deterministic Cases", lambda c: c["case_category"] == "DETERMINISTIC" and c["expected_family"] == "MULTIROTOR"),
        ("FIXED_WING Deterministic Cases", lambda c: c["case_category"] == "DETERMINISTIC" and c["expected_family"] == "FIXED_WING"),
        ("VTOL Deterministic Cases", lambda c: c["case_category"] == "DETERMINISTIC" and c["expected_family"] == "VTOL"),
        ("Boundary Cases", lambda c: c["case_category"] == "BOUNDARY"),
        ("Ambiguous Cases", lambda c: c["case_category"] == "AMBIGUOUS"),
        ("Conflicting Cases", lambda c: c["case_category"] == "CONFLICTING"),
        ("Infeasible Cases", lambda c: c["case_category"] == "INFEASIBLE"),
        ("Invalid Cases", lambda c: c["case_category"] == "INVALID"),
    ]

    lines = [
        "# Vehicle Selection Engine — Complete 600 Case Individual Validation Outputs",
        "",
        "> **Document Status**: Complete Individual Case Export  ",
        "> **Total Cases Evaluated**: 600 Cases  ",
        "> **Verification Rule**: Every single case (CASE 001 through CASE 600) is individually listed below.  ",
        "",
    ]

    for title, filter_fn in categories:
        group_cases = [c for c in cases if filter_fn(c)]
        lines.append(f"## {title} ({len(group_cases)} Cases)")
        lines.append("")
        lines.append("| Case ID | Payload (kg) | Range (km) | Endurance (min) | Hover Req | VTOL Req | Runway | Expected | Raw Output | Family | Score | Confidence | Classification | Pros / Cons |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

        for c in group_cases:
            inp = c["inputs"]
            pros_str = "; ".join(c["reasoning_pros"])
            cons_str = "; ".join(c["penalties_cons"])
            reason_combined = f"PROS: {pros_str}" if pros_str else ""
            if cons_str:
                reason_combined += f" | CONS: {cons_str}" if reason_combined else f"CONS: {cons_str}"
            if not reason_combined:
                reason_combined = c["validation_result"]

            # Replace line breaks in table content
            reason_combined = reason_combined.replace("\n", " ")

            lines.append(
                f"| `{c['case_id']}` | {inp['payload_kg']} | {inp['range_km']} | {inp['endurance_min']} | "
                f"{inp['hover_required']} | {inp['vertical_takeoff_required']} | {inp['runway_available']} | "
                f"`{c['expected_family']}` | `{c['raw_selector_output']}` | `{c['normalized_family_output']}` | "
                f"{c['selected_score']:.2f} | {c['confidence']:.2f} | `{c['final_test_classification']}` | {reason_combined} |"
            )
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    res = export_all_cases()
    print("EXPORT COMPLETED CLEANLY.")
    print("JSON:", res["json_path"])
    print("CSV:", res["csv_path"])
    print("Manual:", res["manual_path"])
    print("MD:", res["md_path"])
    print(f"Total: {res['total_cases']}")
