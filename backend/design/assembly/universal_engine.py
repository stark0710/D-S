"""
Universal Entry Point Subsystem for Torq Wings Design Engine (Phase 13).

Defines TorqWingsDesignEngine, providing the common programmatic interface:
    TorqWingsDesignEngine.generate(aircraft_class, technical_requirements, output_dir=None)

Architecture Guardrails:
    1. DOES NOT parse raw English.
    2. DOES NOT select aircraft architecture; dispatches strictly based on explicitly supplied aircraft_class.
    3. DOES NOT perform duplicate physics.
    4. Validates input schema and output FinalAircraftDesign contract.
    5. Clean extension point for future Multirotor pipeline.
"""

import os
from typing import Any, Dict, Optional, Union
from enum import Enum

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel

from backend.design.assembly.final_design_contract import (
    FinalAircraftDesign,
    AircraftClass,
    OverallDesignStatus,
)
from backend.design.assembly.fixed_wing_adapter import FixedWingDesignAdapter
from backend.design.assembly.vtol_adapter import VTOLDesignAdapter
from backend.design.assembly.report_generator import export_design_json, export_design_markdown


class UnsupportedArchitectureError(ValueError):
    """Raised when an unrecognized or unsupported aircraft architecture is requested."""
    pass


class InvalidTechnicalRequirementsError(ValueError):
    """Raised when input technical requirements are malformed, missing, or contain raw unparsed text."""
    pass


class ContractValidationError(RuntimeError):
    """Raised when the assembled FinalAircraftDesign fails integrity checks."""
    pass


class TorqWingsDesignEngine:
    """
    Universal programmatic entry interface for Torq Wings Design Engine.
    Dispatches to category-specific pipelines and produces normalized FinalAircraftDesign contracts.
    """

    @classmethod
    def generate(
        cls,
        aircraft_class: Union[str, AircraftClass, AircraftType],
        technical_requirements: Union[Dict[str, Any], RequirementModel, VTOLRequirementModel],
        output_dir: Optional[str] = None,
    ) -> FinalAircraftDesign:
        """
        Executes aircraft design synthesis for the explicitly requested aircraft class.

        Args:
            aircraft_class: Target architecture ("FIXED_WING", "VTOL", or "MULTIROTOR").
            technical_requirements: Structured technical requirements (dict or model instance).
            output_dir: Optional directory path to export deterministic JSON and Markdown reports.

        Returns:
            FinalAircraftDesign: Complete, strongly-typed aircraft design specification.

        Raises:
            UnsupportedArchitectureError: If aircraft_class is missing, unknown, or unsupported.
            InvalidTechnicalRequirementsError: If requirements fail schema validation.
            ContractValidationError: If output specification fails completeness checks.
        """
        # 1. Resolve and validate aircraft_class
        norm_class = cls._resolve_aircraft_class(aircraft_class)

        # 2. Check for multirotor extension point (Section 28)
        if norm_class == AircraftClass.MULTIROTOR:
            raise NotImplementedError(
                "Multirotor engineering pipeline extension point established, but Multirotor physics "
                "modules are deferred to a future phase per Phase 13 Section 28 specifications."
            )

        # 3. Validate and convert technical_requirements
        structured_reqs = cls._validate_and_parse_requirements(norm_class, technical_requirements)

        # 4. Dispatch to category pipeline adapter
        if norm_class == AircraftClass.FIXED_WING:
            adapter = FixedWingDesignAdapter()
            design = adapter.run(structured_reqs)
        elif norm_class == AircraftClass.VTOL:
            adapter = VTOLDesignAdapter()
            design = adapter.run(structured_reqs)
        else:
            raise UnsupportedArchitectureError(f"Unhandled aircraft class: '{norm_class}'.")

        # 5. Validate output contract
        cls._validate_contract(design)

        # 5. Optional file export
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            json_path = os.path.join(output_dir, "final_aircraft_design.json")
            md_path = os.path.join(output_dir, "final_aircraft_design.md")
            export_design_json(design, json_path)
            export_design_markdown(design, md_path)

        return design

    @classmethod
    def _resolve_aircraft_class(cls, raw: Any) -> AircraftClass:
        """Resolves raw input to canonical AircraftClass enum."""
        if raw is None:
            raise UnsupportedArchitectureError(
                "aircraft_class is mandatory and must be explicitly specified ('FIXED_WING', 'VTOL')."
            )

        if isinstance(raw, AircraftClass):
            return raw

        if isinstance(raw, AircraftType):
            if raw == AircraftType.FIXED_WING:
                return AircraftClass.FIXED_WING
            elif raw == AircraftType.VTOL:
                return AircraftClass.VTOL
            elif raw in (AircraftType.QUADCOPTER, AircraftType.HEXACOPTER, AircraftType.OCTOCOPTER):
                return AircraftClass.MULTIROTOR

        if isinstance(raw, str):
            clean = raw.strip().upper().replace("-", "_").replace(" ", "_")
            if clean in ("FIXED_WING", "FIXEDWING", "PLANE", "AIRPLANE"):
                return AircraftClass.FIXED_WING
            elif clean in ("VTOL", "QUADPLANE", "LIFT_CRUISE"):
                return AircraftClass.VTOL
            elif clean in ("MULTIROTOR", "DRONE", "QUADCOPTER", "HEXACOPTER"):
                return AircraftClass.MULTIROTOR

        raise UnsupportedArchitectureError(
            f"Unsupported aircraft architecture '{raw}'. Expected 'FIXED_WING', 'VTOL', or 'MULTIROTOR'."
        )

    @classmethod
    def _validate_and_parse_requirements(
        cls,
        target_class: AircraftClass,
        raw_reqs: Any,
    ) -> Any:
        """Validates structured requirements against canonical models."""
        if raw_reqs is None:
            raise InvalidTechnicalRequirementsError("Technical requirements must be provided.")

        # If already a valid model instance
        if target_class == AircraftClass.FIXED_WING and isinstance(raw_reqs, RequirementModel):
            return raw_reqs
        if target_class == AircraftClass.VTOL and isinstance(raw_reqs, VTOLRequirementModel):
            return raw_reqs

        # Reject raw strings (Design Engine does not parse English!)
        if isinstance(raw_reqs, str):
            raise InvalidTechnicalRequirementsError(
                "Design Engine received raw string requirements. Upstream Requirement Agent must parse "
                "English into a structured dictionary or RequirementModel before calling Design Engine."
            )

        if not isinstance(raw_reqs, dict):
            raise InvalidTechnicalRequirementsError(
                f"Expected technical_requirements to be a dict or RequirementModel, got {type(raw_reqs).__name__}."
            )

        # Parse from dictionary
        data = dict(raw_reqs)

        # Support nested structure like {"mission": {...}, "payload": {...}}
        payload_mass = data.get("payload_weight_kg", data.get("payload_mass"))
        if payload_mass is None and "payload" in data and isinstance(data["payload"], dict):
            payload_mass = data["payload"].get("mass_kg", data["payload"].get("mass"))

        range_km = data.get("target_range_km", data.get("target_range"))
        endurance_min = data.get("target_flight_time_min", data.get("target_flight_time"))
        cruise_speed = data.get("cruise_speed_kmh", data.get("cruise_speed"))

        if "mission" in data and isinstance(data["mission"], dict):
            m = data["mission"]
            if range_km is None:
                range_km = m.get("range_km", m.get("target_range_km"))
            if endurance_min is None:
                endurance_min = m.get("endurance_min", m.get("target_flight_time_min"))
            if cruise_speed is None:
                cruise_speed = m.get("cruise_speed_kmh", m.get("cruise_speed"))

        if payload_mass is None:
            raise InvalidTechnicalRequirementsError("Missing required parameter: payload_weight_kg (or payload.mass_kg).")
        if range_km is None and endurance_min is None:
            raise InvalidTechnicalRequirementsError("At least one of range_km or endurance_min must be provided.")

        # Apply realistic defaults for secondary parameters if missing
        if range_km is None:
            range_km = 40.0
        if endurance_min is None:
            endurance_min = 35.0
        if cruise_speed is None:
            cruise_speed = 85.0

        if target_class == AircraftClass.FIXED_WING:
            return RequirementModel(
                mission_type=MissionType.SURVEY,
                payload_weight_kg=float(payload_mass),
                target_flight_time_min=float(endurance_min),
                target_range_km=float(range_km),
                cruise_speed_kmh=float(cruise_speed),
                takeoff_type=TakeoffType.RUNWAY,
                landing_type=LandingType.RUNWAY,
                environment=OperatingEnvironment.RURAL,
                aircraft_type=AircraftType.FIXED_WING,
            )
        elif target_class == AircraftClass.VTOL:
            hover_dur = data.get("hover_duration_min", 5.0)
            if "mission" in data and isinstance(data["mission"], dict):
                hover_dur = data["mission"].get("hover_duration_min", hover_dur)

            return VTOLRequirementModel.create(
                mission_type=MissionType.SURVEY,
                payload_mass=float(payload_mass),
                target_range=float(range_km),
                target_flight_time=float(endurance_min),
                cruise_speed=float(cruise_speed),
                vtol_type=VTOLType.LIFT_CRUISE,
                hover_duration_min=float(hover_dur),
                transition_speed_kmh=data.get("transition_speed_kmh", 65.0),
                lift_motor_count=data.get("lift_motor_count", 4),
                takeoff_type=TakeoffType.VERTICAL,
                landing_type=LandingType.VERTICAL,
                environment=OperatingEnvironment.RURAL,
                optimization_priority=OptimizationPriority.BALANCED,
                design_mode=DesignMode.MANUAL,
            )

        raise UnsupportedArchitectureError(f"Unsupported target class {target_class}")

    @classmethod
    def _validate_contract(cls, design: FinalAircraftDesign) -> None:
        """Validates that the output contract satisfies Section 11 completeness rules."""
        if not design.design_id:
            raise ContractValidationError("FinalAircraftDesign must contain a non-empty design_id.")
        if design.mass_properties.mtow_kg <= 0.0:
            raise ContractValidationError("FinalAircraftDesign has zero or negative MTOW.")
        if not design.cad_handover:
            raise ContractValidationError("FinalAircraftDesign missing CAD handover specification.")
        if not design.simulation_handover:
            raise ContractValidationError("FinalAircraftDesign missing Simulation handover specification.")
        if not design.requirement_traceability:
            raise ContractValidationError("FinalAircraftDesign must contain requirement traceability items.")
        if not design.provenance:
            raise ContractValidationError("FinalAircraftDesign must contain provenance records.")
        if design.validation_status.flight_validated is not False:
            raise ContractValidationError(
                "Violation of Section 10: flight_validated must be False. Empirical flight testing is not validated."
            )
