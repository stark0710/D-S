"""
Multidisciplinary Orchestrator for Fixed-Wing Aircraft Sizing and Design Synthesis.
"""

import logging
from typing import Optional, List

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.validation.requirement_validator import RequirementValidator
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.mission.mission_requirements import (
    MissionRequirements,
    MissionCategory,
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
)
from backend.design.fixed_wing.mission.mission_engine import MissionEngine

from backend.design.fixed_wing.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.fixed_wing.configuration.configuration_engine import ConfigurationEngine
from backend.design.fixed_wing.configuration.configuration_validator import ConfigurationValidationError

from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.fixed_wing.wing.wing_engine import WingEngine
from backend.design.fixed_wing.wing.wing_validator import WingValidationError

from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements
from backend.design.fixed_wing.airfoil.airfoil_engine import AirfoilEngine
from backend.design.fixed_wing.airfoil.airfoil_validator import AirfoilValidationError

from backend.design.fixed_wing.tail.tail_requirements import TailRequirements
from backend.design.fixed_wing.tail.tail_engine import TailEngine
from backend.design.fixed_wing.tail.tail_validator import TailValidationError

from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.fixed_wing.fuselage.fuselage_engine import FuselageEngine
from backend.design.fixed_wing.fuselage.fuselage_validator import FuselageValidationError

from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
from backend.design.fixed_wing.propulsion.propulsion_validator import PropulsionValidationError

from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements
from backend.design.fixed_wing.avionics.avionics_engine import AvionicsEngine

from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements
from backend.design.fixed_wing.payload.payload_engine import PayloadEngine
from backend.design.fixed_wing.payload.payload_validator import PayloadValidationError

from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.fixed_wing.mass_properties.mass_validator import MassValidationError

from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
from backend.design.fixed_wing.flight_performance.flight_performance_engine import FlightPerformanceEngine
from backend.design.fixed_wing.flight_performance.flight_validator import FlightValidationError

from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements
from backend.design.fixed_wing.verification.verification_engine import VerificationEngine

from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.pipeline.pipeline_result import FixedWingDesignResult, PipelineStatus
from backend.design.fixed_wing.pipeline.convergence import (
    ConvergenceEvaluator,
    DEFAULT_CONVERGENCE_TOLERANCE,
    DEFAULT_MAX_ITERATIONS,
)
from backend.design.fixed_wing.pipeline.exceptions import (
    InvalidRequirementsError,
    ConfigurationInfeasibleError,
    SizingInfeasibleError,
    ComponentSelectionError,
    NonConvergenceError,
    VerificationFailedError,
)

logger = logging.getLogger(__name__)


class FixedWingDesignPipeline:
    """
    Multidisciplinary Fixed-Wing Aircraft Synthesis Orchestrator.
    Connects canonical subsystem engines into a convergent sizing loop.
    """

    def __init__(
        self,
        tolerance: float = DEFAULT_CONVERGENCE_TOLERANCE,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        raise_on_failure: bool = False,
    ) -> None:
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.raise_on_failure = raise_on_failure
        self._evaluator = ConvergenceEvaluator(tolerance=tolerance, max_iterations=max_iterations)

        # Initialize Canonical Engines
        self._req_validator = RequirementValidator()
        self._mission_engine = MissionEngine()
        self._configuration_engine = ConfigurationEngine()
        self._wing_engine = WingEngine()
        self._airfoil_engine = AirfoilEngine()
        self._tail_engine = TailEngine()
        self._fuselage_engine = FuselageEngine()
        self._propulsion_engine = PropulsionEngine()
        self._avionics_engine = AvionicsEngine()
        self._payload_engine = PayloadEngine()
        self._mass_properties_engine = MassPropertiesEngine()
        self._flight_performance_engine = FlightPerformanceEngine()
        self._verification_engine = VerificationEngine()

    def execute(self, requirements: RequirementModel) -> FixedWingDesignResult:
        """
        Executes the fixed-wing design synthesis pipeline for the provided requirements.
        """
        context = FixedWingPipelineContext(requirements=requirements)

        # 1. Validate Input Requirements
        if requirements is None or requirements.payload_weight_kg <= 0.0 or requirements.target_range_km <= 0.0 or requirements.target_flight_time_min <= 0.0:
            err_msg = "Invalid requirement input parameters."
            context.errors.append(err_msg)
            if self.raise_on_failure:
                raise InvalidRequirementsError(err_msg)
            return FixedWingDesignResult(
                success=False,
                status=PipelineStatus.INVALID_REQUIREMENTS,
                iterations=0,
                converged=False,
                errors=context.errors,
            )

        try:
            val_res = self._req_validator.validate(requirements)
            if hasattr(val_res, "is_valid") and not val_res.is_valid:
                err_msg = f"Requirement validation failed: {getattr(val_res, 'errors', [])}"
                context.errors.append(err_msg)
                if self.raise_on_failure:
                    raise InvalidRequirementsError(err_msg)
                return FixedWingDesignResult(
                    success=False,
                    status=PipelineStatus.INVALID_REQUIREMENTS,
                    iterations=0,
                    converged=False,
                    errors=context.errors,
                )
        except Exception as e:
            err_msg = f"Requirement validation exception: {e}"
            context.errors.append(err_msg)
            if self.raise_on_failure:
                raise InvalidRequirementsError(err_msg)
            return FixedWingDesignResult(
                success=False,
                status=PipelineStatus.INVALID_REQUIREMENTS,
                iterations=0,
                converged=False,
                errors=context.errors,
            )

        # 2. Mission Requirements Translation & Mission Engine
        try:
            mission_reqs = self._translate_requirements(requirements)
            context.mission_result = self._mission_engine.process_mission(mission_reqs)
        except Exception as e:
            err_msg = f"Mission processing failed: {e}"
            context.errors.append(err_msg)
            if self.raise_on_failure:
                raise InvalidRequirementsError(err_msg)
            return FixedWingDesignResult(
                success=False,
                status=PipelineStatus.INVALID_REQUIREMENTS,
                iterations=0,
                converged=False,
                errors=context.errors,
            )

        # 3. Configuration Engine (CONFIGURATION FREEZE)
        try:
            config_reqs = ConfigurationRequirements(mission_result=context.mission_result)
            context.configuration_result = self._configuration_engine.process_configuration(config_reqs)
        except (ConfigurationValidationError, Exception) as e:
            err_msg = f"Configuration selection failed: {e}"
            context.errors.append(err_msg)
            if self.raise_on_failure:
                raise ConfigurationInfeasibleError(err_msg)
            return FixedWingDesignResult(
                success=False,
                status=PipelineStatus.CONFIGURATION_INFEASIBLE,
                iterations=0,
                converged=False,
                mission_result=context.mission_result,
                errors=context.errors,
            )

        # 4. Establish Initial MTOW Estimate
        initial_mtow = requirements.maximum_takeoff_weight_kg
        if initial_mtow is None or initial_mtow <= 0.0:
            initial_mtow = max(1.5, requirements.payload_weight_kg * 2.5)

        context.current_mtow = initial_mtow
        frozen_config = context.configuration_result

        # 5. Multidisciplinary Iterative Sizing Loop
        from backend.design.fixed_wing.wing.wing_registry import WingStrategyRegistry
        category = context.mission_result.mission_profile.mission_category
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        wing_strategy = WingStrategyRegistry.get(strategy_name)
        target_ar = wing_strategy.get_target_aspect_ratio()
        
        # Determine candidate aspect ratios
        if target_ar >= 12.0:
            ar_candidates = [target_ar, target_ar - 2.0, target_ar - 4.0, target_ar - 6.0]
        elif target_ar >= 7.0:
            ar_candidates = [target_ar, target_ar - 1.0, target_ar - 2.0, target_ar - 3.0]
        else:
            ar_candidates = [target_ar, target_ar - 0.5, target_ar - 1.0]

        best_status = None
        best_iteration = 0
        sizing_success = False
        attempted_ars = []

        for ar_cand in ar_candidates:
            attempted_ars.append(ar_cand)
            # Reset convergence state for this AR candidate
            context.current_mtow = initial_mtow
            context.warnings = [w for w in context.warnings if not w.startswith("AR_RESELECTED:")]
            context.errors = []
            context.convergence_history = []
            
            iteration = 0
            converged = False
            ar_failed = False
            failure_status = None
            
            while iteration < self.max_iterations and not converged:
                iteration += 1
                old_mtow = context.current_mtow
                context.previous_mtow = old_mtow
                context.mission_result.mission_profile.maximum_takeoff_weight_limit_kg = old_mtow
                context.mission_result.constraints.maximum_takeoff_weight_kg = requirements.maximum_takeoff_weight_kg or 25.0
                
                try:
                    # A. Wing Sizing (forcing preferred_aspect_ratio = ar_cand)
                    wing_reqs = WingRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        preferred_aspect_ratio=ar_cand,
                    )
                    context.wing_result = self._wing_engine.process_wing_design(wing_reqs)
                    
                    # B. Airfoil Sizing
                    airfoil_reqs = AirfoilRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                    )
                    context.airfoil_result = self._airfoil_engine.process_airfoil_design(airfoil_reqs)
                    
                    # C. Tail Sizing
                    tail_reqs = TailRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                        airfoil_result=context.airfoil_result,
                    )
                    context.tail_result = self._tail_engine.process_tail_design(tail_reqs)
                    
                    # D. Fuselage Sizing
                    fuselage_reqs = FuselageRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                        airfoil_result=context.airfoil_result,
                        tail_result=context.tail_result,
                    )
                    context.fuselage_result = self._fuselage_engine.process_fuselage_design(fuselage_reqs)
                    
                    # E. Propulsion Sizing
                    propulsion_reqs = PropulsionRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                        airfoil_result=context.airfoil_result,
                        tail_result=context.tail_result,
                        fuselage_result=context.fuselage_result,
                        flight_performance_result=context.performance_result,
                    )
                    context.propulsion_result = self._propulsion_engine.process_propulsion_design(propulsion_reqs)
                    
                    # F. Avionics Sizing
                    avionics_reqs = AvionicsRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                        airfoil_result=context.airfoil_result,
                        tail_result=context.tail_result,
                        fuselage_result=context.fuselage_result,
                        propulsion_result=context.propulsion_result,
                    )
                    context.avionics_result = self._avionics_engine.process_avionics_design(avionics_reqs)
                    
                    # G. Payload Sizing
                    payload_reqs = PayloadRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                        airfoil_result=context.airfoil_result,
                        tail_result=context.tail_result,
                        fuselage_result=context.fuselage_result,
                        propulsion_result=context.propulsion_result,
                        avionics_result=context.avionics_result,
                    )
                    context.payload_result = self._payload_engine.process_payload_design(payload_reqs)
                    
                    # H. Mass Sizing
                    mass_reqs = MassRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                        airfoil_result=context.airfoil_result,
                        tail_result=context.tail_result,
                        fuselage_result=context.fuselage_result,
                        propulsion_result=context.propulsion_result,
                        avionics_result=context.avionics_result,
                        payload_result=context.payload_result,
                    )
                    context.mass_properties_result = self._mass_properties_engine.process_mass_design(mass_reqs)
                    
                    # I. Flight Performance Sizing
                    flight_reqs = FlightRequirements(
                        mission_result=context.mission_result,
                        configuration_result=frozen_config,
                        wing_result=context.wing_result,
                        airfoil_result=context.airfoil_result,
                        tail_result=context.tail_result,
                        fuselage_result=context.fuselage_result,
                        propulsion_result=context.propulsion_result,
                        avionics_result=context.avionics_result,
                        payload_result=context.payload_result,
                        mass_result=context.mass_properties_result,
                    )
                    context.performance_result = self._flight_performance_engine.process_performance_design(flight_reqs)
                    
                except (WingValidationError, AirfoilValidationError, TailValidationError, FuselageValidationError) as e:
                    err_msg = f"Sizing engine validation error at iteration {iteration}: {e}"
                    context.errors.append(err_msg)
                    ar_failed = True
                    failure_status = PipelineStatus.SIZING_INFEASIBLE
                    if "airfoil_structure_incompatible" in str(e).lower():
                        failure_status = PipelineStatus.AIRFOIL_STRUCTURE_INCOMPATIBLE
                    break
                except PropulsionValidationError as e:
                    err_msg = f"Propulsion component selection error at iteration {iteration}: {e}"
                    context.errors.append(err_msg)
                    ar_failed = True
                    failure_status = PipelineStatus.PROPULSION_INFEASIBLE
                    break
                except PayloadValidationError as e:
                    err_msg = f"Payload validation error at iteration {iteration}: {e}"
                    context.errors.append(err_msg)
                    ar_failed = True
                    exc_str = str(e).lower()
                    if "component_database_limitation" in exc_str:
                        failure_status = PipelineStatus.COMPONENT_DATABASE_LIMITATION
                    else:
                        failure_status = PipelineStatus.PAYLOAD_INFEASIBLE
                    break
                except MassValidationError as e:
                    err_msg = f"Mass validation error at iteration {iteration}: {e}"
                    context.errors.append(err_msg)
                    ar_failed = True
                    exc_str = str(e).lower()
                    if "exceeds maximum takeoff weight limit" in exc_str:
                        failure_status = PipelineStatus.MTOW_LIMIT_EXCEEDED
                    elif "cg" in exc_str or "center of gravity" in exc_str:
                        failure_status = PipelineStatus.STABILITY_INFEASIBLE
                    else:
                        failure_status = PipelineStatus.SIZING_INFEASIBLE
                    break
                except FlightValidationError as e:
                    err_msg = f"Flight performance validation error at iteration {iteration}: {e}"
                    context.errors.append(err_msg)
                    ar_failed = True
                    failure_status = PipelineStatus.PERFORMANCE_INFEASIBLE
                    break
                except Exception as e:
                    err_msg = f"Subsystem execution failed at iteration {iteration}: {e}"
                    context.errors.append(err_msg)
                    ar_failed = True
                    exc_str = str(e).lower()
                    if "component_database_limitation" in exc_str:
                        failure_status = PipelineStatus.COMPONENT_DATABASE_LIMITATION
                    elif "communication_infeasible" in exc_str:
                        failure_status = PipelineStatus.COMMUNICATION_INFEASIBLE
                    elif "airfoil_structure_incompatible" in exc_str:
                        failure_status = PipelineStatus.AIRFOIL_STRUCTURE_INCOMPATIBLE
                    elif "propulsion_infeasible" in exc_str:
                        failure_status = PipelineStatus.PROPULSION_INFEASIBLE
                    elif "battery_infeasible" in exc_str:
                        failure_status = PipelineStatus.BATTERY_INFEASIBLE
                    elif "stability_infeasible" in exc_str:
                        failure_status = PipelineStatus.STABILITY_INFEASIBLE
                    elif "performance_infeasible" in exc_str:
                        failure_status = PipelineStatus.PERFORMANCE_INFEASIBLE
                    else:
                        failure_status = PipelineStatus.INTERNAL_EXCEPTION
                    break
                
                # Extract New MTOW and apply relaxation
                wb = context.mass_properties_result.weight_breakdown
                raw_new_mtow = round(wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg, 4)
                relaxed_mtow = round(0.75 * raw_new_mtow + 0.25 * old_mtow, 4)
                context.current_mtow = relaxed_mtow
                
                step_record = self._evaluator.evaluate_step(iteration, old_mtow, relaxed_mtow)
                context.convergence_history.append(step_record)
                converged = step_record.converged

            # If this AR converged successfully without failure
            if not ar_failed and converged:
                sizing_success = True
                if ar_cand != target_ar:
                    warn_msg = f"AR_RESELECTED: Aspect ratio adjusted from initial {target_ar:.1f} to final {ar_cand:.1f} due to structural thickness or packaging limits."
                    if warn_msg not in context.warnings:
                        context.warnings.append(warn_msg)
                break
            else:
                if failure_status is None:
                    failure_status = PipelineStatus.CONVERGENCE_FAILURE
                best_status = failure_status
                best_iteration = iteration

        # Record all attempted ARs in warnings
        context.warnings.append(f"DIAGNOSTICS_AR_ATTEMPTED: {attempted_ars}")

        # If all candidates failed:
        if not sizing_success:
            if self.raise_on_failure:
                if best_status == PipelineStatus.CONVERGENCE_FAILURE:
                    from backend.design.fixed_wing.pipeline.exceptions import NonConvergenceError
                    raise NonConvergenceError(f"Pipeline failed to converge after {best_iteration} iterations.", history=context.convergence_history)
                raise SizingInfeasibleError(f"Sizing infeasible for all aspect ratio candidates: {context.errors}")
            return self._build_result(context, best_status, False, best_iteration)

        if not converged:
            err_msg = f"Pipeline failed to converge after {iteration} iterations."
            context.errors.append(err_msg)
            if self.raise_on_failure:
                raise NonConvergenceError(err_msg, history=context.convergence_history)
            return self._build_result(context, PipelineStatus.CONVERGENCE_FAILURE, False, iteration)

        # 6. Post-Convergence Verification Engine
        try:
            verif_reqs = VerificationRequirements(
                mission_result=context.mission_result,
                configuration_result=frozen_config,
                wing_result=context.wing_result,
                airfoil_result=context.airfoil_result,
                tail_result=context.tail_result,
                fuselage_result=context.fuselage_result,
                propulsion_result=context.propulsion_result,
                avionics_result=context.avionics_result,
                payload_result=context.payload_result,
                mass_result=context.mass_properties_result,
                flight_result=context.performance_result,
            )
            context.verification_result = self._verification_engine.process_verification(verif_reqs)
        except Exception as e:
            err_msg = f"Verification execution error: {e}"
            context.errors.append(err_msg)
            status = PipelineStatus.VERIFICATION_FAILED
            if context.mass_properties_result and not (0.05 <= context.mass_properties_result.static_margin <= 0.25):
                status = PipelineStatus.STABILITY_INFEASIBLE
            if self.raise_on_failure:
                raise VerificationFailedError(err_msg)
            return self._build_result(context, status, True, iteration)

        # Check overall verification compliance
        verif_report = getattr(context.verification_result, "compliance_report", None)
        if verif_report is None:
            verif_passed = False
        else:
            verif_passed = getattr(verif_report, "is_fully_compliant", False)
        if not verif_passed:
            err_msg = "Aircraft design failed verification compliance checks."
            context.errors.append(err_msg)
            status = PipelineStatus.VERIFICATION_FAILED
            if verif_report and hasattr(verif_report, "failed_categories") and verif_report.failed_categories:
                if "Stability" in verif_report.failed_categories:
                    status = PipelineStatus.STABILITY_INFEASIBLE
                elif "Performance" in verif_report.failed_categories:
                    status = PipelineStatus.PERFORMANCE_INFEASIBLE
            if self.raise_on_failure:
                raise VerificationFailedError(err_msg)
            return self._build_result(context, status, True, iteration)

        # 7. Final Success Result Assembly
        return self._build_result(context, PipelineStatus.SUCCESS, True, iteration)

    def _translate_requirements(self, req: RequirementModel) -> MissionRequirements:
        """
        Translates canonical RequirementModel to subsystem MissionRequirements.
        """
        cat_map = {
            MissionType.MAPPING: MissionCategory.MAPPING,
            MissionType.SURVEY: MissionCategory.SURVEY,
            MissionType.DELIVERY: MissionCategory.CARGO,
            MissionType.AGRICULTURE: MissionCategory.AGRICULTURE,
            MissionType.RESEARCH: MissionCategory.RESEARCH,
            MissionType.SECURITY: MissionCategory.SURVEILLANCE,
            MissionType.MILITARY: MissionCategory.SURVEILLANCE,
            MissionType.INSPECTION: MissionCategory.SURVEILLANCE,
            MissionType.DISASTER_RESPONSE: MissionCategory.SURVEY,
        }
        category = cat_map.get(req.mission_type, MissionCategory.SURVEY)

        to_map = {
            TakeoffType.CATAPULT: LaunchMethod.CATAPULT,
            TakeoffType.HAND_LAUNCH: LaunchMethod.HAND_LAUNCH,
            TakeoffType.RUNWAY: LaunchMethod.RUNWAY,
        }
        launch = to_map.get(req.takeoff_type, LaunchMethod.CATAPULT if req.payload_weight_kg <= 3.0 else LaunchMethod.RUNWAY)

        ld_map = {
            LandingType.BELLY_LANDING: LandingMethod.BELLY_LANDING,
            LandingType.PARACHUTE: LandingMethod.PARACHUTE,
            LandingType.RUNWAY: LandingMethod.RUNWAY,
            LandingType.NET_RECOVERY: LandingMethod.NET_RECOVERY,
        }
        landing = ld_map.get(req.landing_type, LandingMethod.BELLY_LANDING if req.payload_weight_kg <= 3.0 else LandingMethod.RUNWAY)

        env_map = {
            OperatingEnvironment.RURAL: EnvironmentType.RURAL,
            OperatingEnvironment.URBAN: EnvironmentType.URBAN,
            OperatingEnvironment.FOREST: EnvironmentType.FOREST,
            OperatingEnvironment.MOUNTAIN: EnvironmentType.MOUNTAIN,
            OperatingEnvironment.DESERT: EnvironmentType.DESERT,
            OperatingEnvironment.MARINE: EnvironmentType.MARINE,
        }
        env = env_map.get(req.environment, EnvironmentType.RURAL)

        mtow_limit = req.maximum_takeoff_weight_kg
        if mtow_limit is None or mtow_limit <= 0.0:
            mtow_limit = max(2.0, req.payload_weight_kg * 3.0)

        return MissionRequirements(
            mission_category=category,
            payload_kg=req.payload_weight_kg,
            flight_time_min=req.target_flight_time_min,
            cruise_speed_kmh=req.cruise_speed_kmh,
            stall_speed_target_kmh=45.0,
            maximum_takeoff_weight_limit_kg=mtow_limit,
            operational_altitude_m=150.0,
            mission_range_km=req.target_range_km,
            launch_method=launch,
            landing_method=landing,
            budget=req.budget if req.budget else 15000.0,
            environment=env,
            autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        )

    def _build_result(
        self, context: FixedWingPipelineContext, status: PipelineStatus, converged: bool, iterations: int
    ) -> FixedWingDesignResult:
        """
        Assembles FixedWingDesignResult from context state.
        """
        success = status == PipelineStatus.SUCCESS
        return FixedWingDesignResult(
            success=success,
            status=status,
            iterations=iterations,
            converged=converged,
            convergence_history=context.convergence_history,
            mission_result=context.mission_result,
            configuration_result=context.configuration_result,
            wing_result=context.wing_result,
            airfoil_result=context.airfoil_result,
            tail_result=context.tail_result,
            fuselage_result=context.fuselage_result,
            propulsion_result=context.propulsion_result,
            avionics_result=context.avionics_result,
            payload_result=context.payload_result,
            mass_properties_result=context.mass_properties_result,
            performance_result=context.performance_result,
            verification_result=context.verification_result,
            warnings=context.warnings,
            errors=context.errors,
        )
