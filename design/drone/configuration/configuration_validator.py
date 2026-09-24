"""
ConfigurationValidator Subsystem

Purpose:
    Defines the `ConfigurationValidator` class responsible for validating multirotor configuration candidates against constraints.

Role in Architecture:
    `ConfigurationValidator` evaluates frame feasibility, motor loss redundancy limits, and physical rotor count bounds.
"""

from backend.design.drone.configuration.configuration_candidate import ConfigurationCandidate
from backend.design.drone.configuration.configuration_constraints import ConfigurationConstraints


class ConfigurationValidator:
    """
    Validator for multirotor configuration candidates.

    Design Principles:
        - Single Responsibility Principle: Multirotor frame constraint and feasibility validation only.
    """

    def validate_candidate(
        self,
        candidate: ConfigurationCandidate,
        constraints: ConfigurationConstraints
    ) -> list[str]:
        """
        Validates a ConfigurationCandidate against ConfigurationConstraints.

        Args:
            candidate (ConfigurationCandidate): Target candidate object.
            constraints (ConfigurationConstraints): Evaluation constraints.

        Returns:
            list[str]: List of warning or incompatibility messages.
        """
        warnings: list[str] = []
        prof = candidate.profile

        if prof.rotor_count < constraints.min_rotors:
            warnings.append(f"Rotor count ({prof.rotor_count}) is below minimum allowed ({constraints.min_rotors}).")

        if prof.rotor_count > constraints.max_rotors:
            warnings.append(f"Rotor count ({prof.rotor_count}) exceeds maximum allowed ({constraints.max_rotors}).")

        if prof.coaxial and not constraints.allow_coaxial:
            warnings.append(f"Coaxial configuration '{prof.config_type}' is disallowed by current constraints.")

        if constraints.required_redundancy in ("SINGLE", "HEXA_SINGLE_FAIL") and prof.rotor_count < 6:
            warnings.append(f"Quadrotor configuration '{prof.config_type}' lacks single motor loss redundancy.")

        if constraints.required_redundancy in ("DUAL", "OCTO_DUAL_FAIL") and prof.rotor_count < 8:
            warnings.append(f"Configuration '{prof.config_type}' with {prof.rotor_count} rotors lacks dual motor loss redundancy.")

        return warnings
