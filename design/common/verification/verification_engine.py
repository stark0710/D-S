from typing import Dict, Any, List
from backend.design.common.verification.verification_context import VerificationContext
from backend.design.common.verification.certification_report import AircraftCertificationReport
from backend.design.common.verification.rule_registry import global_registry
from backend.design.common.verification.rule_loader import RuleLoader
from backend.design.common.verification.rule_engine import RuleEngine

class VerificationEngine:
    def __init__(self):
        # Dynamically load registered rules
        RuleLoader.load_rules_from_directory()
        self.rule_engine = RuleEngine()

    def verify_aircraft(self, 
                        mission_requirements: Any, 
                        final_specification: Any, 
                        subsystem_specifications: Dict[str, Any], 
                        convergence_report: Dict[str, Any] = None) -> AircraftCertificationReport:
        """Runs verification rules against the aircraft design context."""
        # Determine configuration layout/type
        config_type = "Generic"
        if final_specification:
            if hasattr(final_specification, "layout"):
                config_type = final_specification.layout
            elif isinstance(final_specification, dict) and "layout" in final_specification:
                config_type = final_specification["layout"]

        # Parse contexts
        context = VerificationContext(
            mission_requirements=mission_requirements,
            final_specification=final_specification,
            subsystem_specifications=subsystem_specifications,
            convergence_report=convergence_report
        )

        # Get relevant rules
        rules = global_registry.get_rules(config_type)

        # Build summaries for reporting
        aircraft_summary = self._build_aircraft_summary(final_specification, subsystem_specifications)
        mission_summary = self._build_mission_summary(mission_requirements)

        if not final_specification:
            # Sizing failed completely
            return AircraftCertificationReport(
                aircraft_summary=aircraft_summary,
                mission_summary=mission_summary,
                results=[],
                feasible=False
            )

        # Execute rules
        results = self.rule_engine.execute_rules(context, rules)

        return AircraftCertificationReport(
            aircraft_summary=aircraft_summary,
            mission_summary=mission_summary,
            results=results,
            feasible=True
        )

    def _build_aircraft_summary(self, spec: Any, subsystem_specs: Dict[str, Any]) -> Dict[str, Any]:
        summary = {
            "layout": "N/A",
            "mtow_kg": 0.0,
            "empty_weight_kg": 0.0,
            "payload_capacity_kg": 0.0
        }
        if spec:
            summary["layout"] = getattr(spec, "layout", summary["layout"])
            summary["mtow_kg"] = getattr(spec, "mtow_kg", getattr(spec, "mtow", 0.0))
            summary["empty_weight_kg"] = getattr(spec, "empty_weight_kg", 0.0)
            
            # extract payload
            if "PayloadPackagingSpecification" in subsystem_specs:
                p_spec = subsystem_specs["PayloadPackagingSpecification"]
                summary["payload_capacity_kg"] = getattr(p_spec, "payload_mass_kg", getattr(p_spec, "payload_mass", 0.0))
            elif "PayloadPackagingOptimizer" in subsystem_specs:
                p_spec = subsystem_specs["PayloadPackagingOptimizer"]
                summary["payload_capacity_kg"] = getattr(p_spec, "payload_mass_kg", getattr(p_spec, "payload_mass", 0.0))
        return summary

    def _build_mission_summary(self, reqs: Any) -> Dict[str, Any]:
        summary = {
            "category": "N/A",
            "required_payload_kg": 0.0,
            "required_range_km": 0.0,
            "required_endurance_min": 0.0
        }
        if reqs:
            # Check for mission profile fields
            if hasattr(reqs, "mission_category"):
                summary["category"] = reqs.mission_category
            elif hasattr(reqs, "category"):
                summary["category"] = reqs.category

            # Check constraints or targets
            constraints = getattr(reqs, "constraints", None)
            if constraints:
                summary["required_payload_kg"] = getattr(constraints, "minimum_payload_kg", 0.0)
                summary["required_range_km"] = getattr(constraints, "minimum_range_km", 0.0)
                summary["required_endurance_min"] = getattr(constraints, "minimum_endurance_min", 0.0)
            else:
                summary["required_payload_kg"] = getattr(reqs, "payload_kg", 0.0)
                summary["required_range_km"] = getattr(reqs, "mission_range_km", 0.0)
                summary["required_endurance_min"] = getattr(reqs, "flight_time_min", 0.0)
        return summary
