from .mass_requirements import MassRequirements
from .mass_profile import MassProfile
from .mass_constraints import MassConstraints
from .mass_result import MassResult
from .mass_registry import MassRegistry
from .mass_validator import MassValidator
from .authoritative_mass import (
    AuthoritativeMassModel,
    AuthoritativeMassResult,
    ConvergenceStatus,
)

class MassPropertiesEngine:
    """
    Façade manager coordinating VTOL weight distributions, authoritative mass synthesis,
    longitudinal CG evaluation, and multidisciplinary convergence.
    """
    def __init__(self, profile: MassProfile = None, constraints: MassConstraints = None):
        self.profile = profile or MassProfile()
        self.constraints = constraints or MassConstraints()

    def design(self, requirements: MassRequirements) -> MassResult:
        strategy = MassRegistry.get_strategy(requirements.mission_result.mission_profile.mission_category)
        result = strategy.design_mass_properties(requirements, self.profile)
        
        # Phase 5 Authoritative Mass & CG Synthesis
        sizing_mass = float(
            requirements.metadata.get("sizing_mass_kg")
            or getattr(requirements.mission_result.mission_analysis, "estimated_mtow_kg", 25.0)
        )
        n_lift = 4
        if hasattr(requirements, "lift_system_result") and requirements.lift_system_result:
            rl = getattr(requirements.lift_system_result, "rotor_layout", None)
            if rl and hasattr(rl, "rotors") and rl.rotors:
                n_lift = len(rl.rotors)
        if "lift_motor_count" in requirements.metadata and requirements.metadata["lift_motor_count"]:
            n_lift = int(requirements.metadata["lift_motor_count"])

        mac_m = None
        x_lemac = None
        if hasattr(requirements, "wing_result") and requirements.wing_result:
            if hasattr(requirements.wing_result, "wing_geometry"):
                mac_m = getattr(requirements.wing_result.wing_geometry, "mean_aerodynamic_chord_m", 0.40)
                root_c = getattr(requirements.wing_result.wing_geometry, "root_chord_m", 0.30)
                x_lemac = AuthoritativeMassModel.DEFAULT_WING_X_M - 0.25 * (mac_m or 0.40)

        ledger = AuthoritativeMassModel.synthesize_component_masses(
            sizing_mass_kg=sizing_mass,
            lift_motor_count=n_lift,
            wing_result=requirements.wing_result,
            fuselage_result=requirements.fuselage_result,
            tail_result=requirements.tail_result,
            lift_system_result=requirements.lift_system_result,
            forward_propulsion_result=requirements.forward_propulsion_result,
            electrical_result=requirements.electrical_result,
            avionics_result=requirements.avionics_result,
            payload_result=requirements.payload_result,
            mission_result=requirements.mission_result,
            fixed_wing_subsystems=requirements.fixed_wing_subsystems,
            overrides=requirements.metadata.get("mass_overrides", {}),
        )

        cg_res = AuthoritativeMassModel.calculate_center_of_gravity(
            mass_ledger=ledger,
            mac_m=mac_m,
            x_lemac_m=x_lemac,
        )

        residual_val = abs(ledger.total_mass_kg - sizing_mass)
        is_converged = residual_val <= requirements.convergence_tolerance_kg
        conv_status = ConvergenceStatus.CONVERGED if is_converged else ConvergenceStatus.ITERATING

        auth_mass_result = AuthoritativeMassResult(
            sizing_mass_kg=sizing_mass,
            converged_mtow_kg=ledger.total_mass_kg,
            empty_weight_kg=ledger.category_breakdown.empty_mass_kg,
            payload_weight_kg=ledger.category_breakdown.payload_mass_kg,
            battery_weight_kg=ledger.category_breakdown.battery_mass_kg,
            mass_ledger=ledger,
            center_of_gravity=cg_res,
            convergence_status=conv_status,
            is_converged_mtow=is_converged,
            convergence_iterations=requirements.metadata.get("iteration", 1),
            convergence_residual_kg=residual_val,
            convergence_tolerance_kg=requirements.convergence_tolerance_kg,
            relaxation_alpha=requirements.relaxation_alpha,
            status="IMPLEMENTED",
            warnings=list(ledger.unresolved_components),
        )
        result.authoritative_mass_result = auth_mass_result

        errors = MassValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)
            
        return result
