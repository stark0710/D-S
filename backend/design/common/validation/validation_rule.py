"""
ValidationRule Subsystem

Purpose:
    Defines the abstract `ValidationRule` interface and concrete validation rule implementations.

Role in Architecture:
    Each validation rule evaluates a single specific concern on a `RequirementModel` instance.
    This extensible rule structure enforces the Single Responsibility Principle and Open/Closed Principle.
"""

from abc import ABC, abstractmethod
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.validation.validation_code import ValidationCode
from backend.design.common.validation.validation_severity import ValidationSeverity
from backend.design.common.validation.validation_issue import ValidationIssue


class ValidationRule(ABC):
    """
    Abstract base class for requirement validation rules.
    """

    @abstractmethod
    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        """
        Validates a specific requirement concern.

        Args:
            requirements (RequirementModel): Target requirement instance.

        Returns:
            list[ValidationIssue]: Identified validation issues, if any.
        """
        pass


class PayloadValidationRule(ValidationRule):
    """Validates that payload_weight_kg is strictly positive (> 0)."""

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if requirements.payload_weight_kg <= 0:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.INVALID_PAYLOAD,
                    severity=ValidationSeverity.ERROR,
                    field_name="payload_weight_kg",
                    message=f"Payload weight must be greater than 0 kg. Provided: {requirements.payload_weight_kg} kg.",
                    recommendation="Specify a positive payload mass in kilograms (e.g., 2.5 kg)."
                )
            )
        return issues


class FlightTimeValidationRule(ValidationRule):
    """Validates that target_flight_time_min is strictly positive (> 0)."""

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if requirements.target_flight_time_min <= 0:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.INVALID_FLIGHT_TIME,
                    severity=ValidationSeverity.ERROR,
                    field_name="target_flight_time_min",
                    message=f"Target flight time must be greater than 0 minutes. Provided: {requirements.target_flight_time_min} min.",
                    recommendation="Specify a positive target endurance in minutes (e.g., 30 minutes)."
                )
            )
        return issues


class RangeValidationRule(ValidationRule):
    """Validates that target_range_km is strictly positive (> 0)."""

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if requirements.target_range_km <= 0:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.INVALID_RANGE_REQUIREMENT,
                    severity=ValidationSeverity.ERROR,
                    field_name="target_range_km",
                    message=f"Target range must be greater than 0 km. Provided: {requirements.target_range_km} km.",
                    recommendation="Specify a positive target range in kilometers (e.g., 20 km)."
                )
            )
        return issues


class CruiseSpeedValidationRule(ValidationRule):
    """Validates that cruise_speed_kmh is strictly positive (> 0)."""

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if requirements.cruise_speed_kmh <= 0:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.INVALID_CRUISE_SPEED,
                    severity=ValidationSeverity.ERROR,
                    field_name="cruise_speed_kmh",
                    message=f"Cruise speed must be greater than 0 km/h. Provided: {requirements.cruise_speed_kmh} km/h.",
                    recommendation="Specify a positive cruise speed in km/h (e.g., 60 km/h)."
                )
            )
        return issues


class BudgetValidationRule(ValidationRule):
    """Validates that financial budget, if provided, is strictly positive (> 0)."""

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if requirements.budget is not None and requirements.budget <= 0:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.INVALID_BUDGET,
                    severity=ValidationSeverity.ERROR,
                    field_name="budget",
                    message=f"Financial budget must be greater than $0 if specified. Provided: ${requirements.budget}.",
                    recommendation="Specify a positive financial budget or leave budget as None."
                )
            )
        return issues


class TakeoffWeightValidationRule(ValidationRule):
    """Validates that maximum_takeoff_weight_kg, if provided, is greater than payload_weight_kg."""

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if requirements.maximum_takeoff_weight_kg is not None:
            if requirements.maximum_takeoff_weight_kg <= 0:
                issues.append(
                    ValidationIssue(
                        code=ValidationCode.INVALID_TAKEOFF_WEIGHT,
                        severity=ValidationSeverity.ERROR,
                        field_name="maximum_takeoff_weight_kg",
                        message=f"Maximum takeoff weight limit must be greater than 0 kg. Provided: {requirements.maximum_takeoff_weight_kg} kg.",
                        recommendation="Specify a positive MTOW limit in kilograms."
                    )
                )
            elif requirements.maximum_takeoff_weight_kg <= requirements.payload_weight_kg:
                issues.append(
                    ValidationIssue(
                        code=ValidationCode.INVALID_TAKEOFF_WEIGHT,
                        severity=ValidationSeverity.ERROR,
                        field_name="maximum_takeoff_weight_kg",
                        message=(
                            f"Maximum takeoff weight limit ({requirements.maximum_takeoff_weight_kg} kg) must be "
                            f"greater than payload weight ({requirements.payload_weight_kg} kg)."
                        ),
                        recommendation="Increase maximum takeoff weight limit to allow room for airframe, propulsion, and battery mass."
                    )
                )
        return issues


class AircraftSelectionRule(ValidationRule):
    """
    Validates aircraft type selection based on design mode.
    - In MANUAL mode: aircraft_type is mandatory.
    - In ENGINEERING_ADVISOR mode: aircraft_type is optional.
    """

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if requirements.design_mode == DesignMode.MANUAL and requirements.aircraft_type is None:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.AIRCRAFT_TYPE_REQUIRED,
                    severity=ValidationSeverity.ERROR,
                    field_name="aircraft_type",
                    message="Aircraft type must be explicitly specified when executing in MANUAL design mode.",
                    recommendation="Select an aircraft category (e.g., QUADCOPTER, FIXED_WING, VTOL) or switch to ENGINEERING_ADVISOR mode."
                )
            )
        return issues


class TakeoffLandingRule(ValidationRule):
    """Validates compatibility between takeoff and landing operational modes."""

    def validate(self, requirements: RequirementModel) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        # Hand launch or catapult launch with vertical landing requires hybrid or parachute/belly/net recovery
        if requirements.takeoff_type in (TakeoffType.HAND_LAUNCH, TakeoffType.CATAPULT):
            if requirements.landing_type == LandingType.VERTICAL:
                issues.append(
                    ValidationIssue(
                        code=ValidationCode.INVALID_TAKEOFF_LANDING_COMBINATION,
                        severity=ValidationSeverity.WARNING,
                        field_name="landing_type",
                        message=(
                            f"Takeoff type '{requirements.takeoff_type.value}' combined with Vertical landing "
                            f"is uncommon for conventional aircraft unless configuring a hybrid VTOL platform."
                        ),
                        recommendation="Ensure a hybrid VTOL platform is intended, or select PARACHUTE, BELLY_LANDING, or RUNWAY recovery."
                    )
                )
        return issues
