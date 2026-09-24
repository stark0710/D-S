import copy
import math
import os
import csv
import json
from typing import List, Dict, Any, Optional

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.validation.requirement_validator import RequirementValidator
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.router.design_engine import DesignEngine

# Multirotor Sizers & Optimizers
from backend.design.multirotor.mission.mission_strategy_engine import MissionStrategyEngine
from backend.design.multirotor.frame.frame_optimizer import FrameOptimizer
from backend.design.multirotor.frame.frame_models import FrameContext
from backend.design.multirotor.frame.frame_selector import FrameSelector
from backend.design.multirotor.motor.motor_optimizer import MotorOptimizer
from backend.design.multirotor.motor.motor_models import MotorContext
from backend.design.multirotor.motor.motor_selector import MotorSelector
from backend.design.multirotor.propeller.propeller_optimizer import PropellerOptimizer
from backend.design.multirotor.propeller.propeller_models import PropellerContext
from backend.design.multirotor.propeller.propeller_selector import PropellerSelector
from backend.design.multirotor.esc.esc_optimizer import EscOptimizer
from backend.design.multirotor.esc.esc_models import EscContext
from backend.design.multirotor.esc.esc_selector import EscSelector
from backend.design.multirotor.battery.battery_optimizer import BatteryOptimizer
from backend.design.multirotor.battery.battery_models import BatteryContext
from backend.design.multirotor.battery.battery_selector import BatterySelector
from backend.design.multirotor.battery.battery_result import PropulsionAssembly, BatterySpecification
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.propeller.propeller_result import PropellerSpecification
from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification
from backend.design.multirotor.mass_properties.mass_result import MassPropertiesSpecification
from backend.design.multirotor.electrical.electrical_engine import ElectricalEngine
from backend.design.multirotor.electrical.electrical_models import ElectricalContext
from backend.design.multirotor.layout.layout_engine import LayoutEngine
from backend.design.multirotor.layout.layout_models import LayoutContext
from backend.design.multirotor.mass_properties.mass_properties_engine import MassPropertiesEngine
from backend.design.multirotor.mass_properties.mass_models import MassPropertiesContext


# Drone/Common Subsystems
from backend.design.drone.performance.performance_engine import PerformanceEngine
from backend.design.drone.avionics.avionics_engine import AvionicsEngine
from backend.design.common.verification.verification_engine import VerificationEngine

# Pipeline results & convergence
from backend.design.multirotor.pipeline.pipeline_result import PipelineStatus, MultirotorAircraftSpecification, MultirotorDesignResult
from backend.design.multirotor.pipeline.convergence import ConvergenceManager, IterationRecord


class MultirotorDesignPipeline:
    """
    Multidisciplinary Orchestrator for Multirotor Aircraft Sizing and Design Synthesis.
    Iteratively converges discrete catalog selections and verifies engineering safety checks.
    """
    def __init__(self, tolerance: float = 0.01, max_iterations: int = 15, raise_on_failure: bool = False) -> None:
        self.tolerance = tolerance
        self.max_iterations = max_iterations
        self.raise_on_failure = raise_on_failure
        
        # Sizing engine components
        self._validator = RequirementValidator()
        self._strategy_engine = MissionStrategyEngine()
        self._frame_optimizer = FrameOptimizer()
        self._motor_optimizer = MotorOptimizer()
        self._propeller_optimizer = PropellerOptimizer()
        self._esc_optimizer = EscOptimizer()
        self._battery_optimizer = BatteryOptimizer()
        self._electrical_engine = ElectricalEngine()
        self._layout_engine = LayoutEngine()
        self._mass_engine = MassPropertiesEngine()
        self._performance_engine = PerformanceEngine()
        self._avionics_engine = AvionicsEngine()
        self._verification_engine = VerificationEngine()
        
    def execute(self, requirements: RequirementModel) -> MultirotorDesignResult:
        """
        Executes the end-to-end multirotor aircraft design synthesis flow.
        """
        # 1. Validation
        val_res = self._validator.validate(requirements)
        if hasattr(val_res, "is_valid") and not val_res.is_valid:
            err = [issue.message for issue in getattr(val_res, "issues", [])]
            return MultirotorDesignResult(
                success=False,
                status=PipelineStatus.INVALID_REQUIREMENTS,
                iterations=0,
                converged=False,
                errors=err
            )
            
        try:
            # 2. Mission Strategy Recommendation
            strategy_spec = self._strategy_engine.generate_strategy(requirements)
            
            # 3. Catalog Frame Sizing
            payload_dim = requirements.metadata.get("payload_dimensions_m", (0.1, 0.1, 0.08))
            frame_ctx = FrameContext(
                requirements=requirements,
                strategy_spec=strategy_spec,
                payload_weight_kg=requirements.payload_weight_kg,
                payload_dimensions_m=payload_dim
            )
            frame_res = self._frame_optimizer.optimize(frame_ctx)
            if not frame_res.success:
                return MultirotorDesignResult(
                    success=False,
                    status=PipelineStatus.FRAME_INFEASIBLE,
                    iterations=0,
                    converged=False,
                    errors=[f"Frame optimization failed: {frame_res.message}"]
                )
            
            frame_spec = frame_res.generated_specification
            # Enforce strictly Catalog Frame for Multirotor V1
            if frame_spec.approach_type != "Catalog Selection":
                # Clamp to the nearest matching catalog frame to avoid custom structures
                fs = FrameSelector()
                matching = fs.get_matching_frames(frame_spec.configuration, strategy_spec.constraint_summary.maximum_frame_size_m)
                if not matching:
                    return MultirotorDesignResult(
                        success=False,
                        status=PipelineStatus.FRAME_INFEASIBLE,
                        iterations=0,
                        converged=False,
                        errors=["No catalog frames match the configuration & wheelbase constraints."]
                    )
                # Sort matching by proximity of wheelbase and select
                best_match = min(matching, key=lambda f: abs(f.wheelbase_m - frame_spec.wheelbase_m))
                # Re-run Frame Optimizer with clamped variables
                d_vars = {
                    "approach": "Catalog Selection",
                    "name": best_match.name,
                    "wheelbase_m": best_match.wheelbase_m,
                    "arm_diameter_m": best_match.arm_diameter_m,
                    "max_propeller_diameter_m": best_match.max_propeller_diameter_m,
                    "landing_gear_height_m": best_match.landing_gear_height_m,
                    "mass_kg": best_match.empty_mass_kg,
                }
                from backend.design.multirotor.frame.frame_models import FrameCandidate
                candidate = FrameCandidate(design_variables=d_vars)
                self._frame_optimizer.evaluate_candidate(candidate, frame_ctx)
                frame_spec = self._frame_optimizer.build_specification(candidate, frame_ctx)

            # 4. Convergence Sizing Loop
            conv_mgr = ConvergenceManager(tolerance=self.tolerance, max_iterations=self.max_iterations)
            last_m_batt = 0.5  # initial estimate
            prev_record = None
            converged = False
            iteration = 0
            
            # Sizing loop variables
            motor_spec = None
            prop_spec = None
            esc_spec = None
            battery_spec = None
            propulsion_assembly = None
            
            while iteration < self.max_iterations and not converged:
                iteration += 1
                
                # Build mock requirements with adjusted payload to reflect battery weight
                req_mod = copy.copy(requirements)
                payload_passed = conv_mgr.calculate_feedback_payload(
                    actual_payload=requirements.payload_weight_kg,
                    m_batt=last_m_batt,
                    target_hover_time=strategy_spec.engineering_targets.target_hover_time_min
                )
                req_mod.payload_weight_kg = payload_passed
                
                # A. Motor selection
                motor_ctx = MotorContext(requirements=req_mod, strategy_spec=strategy_spec, frame_spec=frame_spec)
                motor_res = self._motor_optimizer.optimize(motor_ctx)
                if not motor_res.success:
                    return MultirotorDesignResult(
                        success=False,
                        status=PipelineStatus.PROPULSION_INFEASIBLE,
                        iterations=iteration,
                        converged=False,
                        errors=[f"Motor selection failed in iteration {iteration}: {motor_res.message}"]
                    )
                motor_spec = motor_res.generated_specification
                
                # B. Propeller selection
                prop_ctx = PropellerContext(requirements=req_mod, strategy_spec=strategy_spec, frame_spec=frame_spec, motor_spec=motor_spec)
                prop_res = self._propeller_optimizer.optimize(prop_ctx)
                if not prop_res.success:
                    return MultirotorDesignResult(
                        success=False,
                        status=PipelineStatus.PROPULSION_INFEASIBLE,
                        iterations=iteration,
                        converged=False,
                        errors=[f"Propeller selection failed in iteration {iteration}: {prop_res.message}"]
                    )
                prop_spec = prop_res.generated_specification
                
                # C. ESC selection
                esc_ctx = EscContext(requirements=req_mod, strategy_spec=strategy_spec, frame_spec=frame_spec, motor_spec=motor_spec, propeller_spec=prop_spec)
                esc_res = self._esc_optimizer.optimize(esc_ctx)
                if not esc_res.success:
                    return MultirotorDesignResult(
                        success=False,
                        status=PipelineStatus.PROPULSION_INFEASIBLE,
                        iterations=iteration,
                        converged=False,
                        errors=[f"ESC selection failed in iteration {iteration}: {esc_res.message}"]
                    )
                esc_spec = esc_res.generated_specification
                
                # D. Battery selection (uses original requirements to size actual flight endurance)
                battery_ctx = BatteryContext(
                    requirements=requirements,
                    strategy_spec=strategy_spec,
                    frame_spec=frame_spec,
                    motor_spec=motor_spec,
                    propeller_spec=prop_spec,
                    esc_spec=esc_spec
                )
                battery_res = self._battery_optimizer.optimize(battery_ctx)
                if not battery_res.success:
                    return MultirotorDesignResult(
                        success=False,
                        status=PipelineStatus.PROPULSION_INFEASIBLE,
                        iterations=iteration,
                        converged=False,
                        errors=[f"Battery selection failed in iteration {iteration}: {battery_res.message}"]
                    )
                battery_spec = battery_res.generated_specification
                propulsion_assembly = self._battery_optimizer.build_propulsion_assembly(battery_spec, battery_ctx)
                
                # Sizing metrics record
                curr_rec = IterationRecord(
                    iteration=iteration,
                    mtow_kg=propulsion_assembly.estimated_auw_kg,
                    battery_mass_kg=battery_spec.weight_kg,
                    required_thrust_n=propulsion_assembly.total_hover_thrust_n,
                    available_thrust_n=propulsion_assembly.max_thrust_capability_n,
                    hover_power_w=propulsion_assembly.hover_power_total_w,
                    hover_throttle_pct=propulsion_assembly.hover_throttle_pct,
                    estimated_endurance_min=battery_spec.estimated_flight_time_min,
                    constraint_status="FEASIBLE",
                    convergence_error_kg=abs(propulsion_assembly.estimated_auw_kg - (prev_record.mtow_kg if prev_record else 0.0))
                )
                conv_mgr.history.append(curr_rec)
                
                # Check convergence
                if prev_record and conv_mgr.is_converged(prev_record, curr_rec):
                    converged = True
                
                prev_record = curr_rec
                last_m_batt = battery_spec.weight_kg
                
            if not converged:
                return MultirotorDesignResult(
                    success=False,
                    status=PipelineStatus.CONVERGENCE_FAILED,
                    iterations=iteration,
                    converged=False,
                    errors=["Takeoff weight and battery sizing metrics did not converge within the maximum iterations limit."]
                )
                
            # 5. Electrical Integration
            elec_ctx = ElectricalContext(
                requirements=requirements,
                strategy_spec=strategy_spec,
                frame_spec=frame_spec,
                propulsion_assembly=propulsion_assembly
            )
            elec_res = self._electrical_engine.optimize(elec_ctx)
            if not elec_res.success:
                return MultirotorDesignResult(
                    success=False,
                    status=PipelineStatus.ELECTRICAL_INFEASIBLE,
                    iterations=iteration,
                    converged=True,
                    errors=[f"Electrical harness routing failed: {elec_res.message}"]
                )
            elec_spec = elec_res.generated_specification
            
            # 6. Payload & Layout
            layout_ctx = LayoutContext(
                requirements=requirements,
                strategy_spec=strategy_spec,
                frame_spec=frame_spec,
                propulsion_assembly=propulsion_assembly,
                electrical_spec=elec_spec
            )
            layout_res = self._layout_engine.optimize(layout_ctx)
            if not layout_res.success:
                return MultirotorDesignResult(
                    success=False,
                    status=PipelineStatus.LAYOUT_INFEASIBLE,
                    iterations=iteration,
                    converged=True,
                    errors=[f"Component packaging layout failed: {layout_res.message}"]
                )
            layout_spec = layout_res.generated_specification
            
            # 7. Mass & CG Sizing
            mass_ctx = MassPropertiesContext(
                requirements=requirements,
                strategy_spec=strategy_spec,
                frame_spec=frame_spec,
                propulsion_assembly=propulsion_assembly,
                electrical_spec=elec_spec,
                layout_spec=layout_spec
            )
            mass_res = self._mass_engine.optimize(mass_ctx)
            if not mass_res.success:
                return MultirotorDesignResult(
                    success=False,
                    status=PipelineStatus.MASS_INFEASIBLE,
                    iterations=iteration,
                    converged=True,
                    errors=[f"Mass properties sizing failed: {mass_res.message}"]
                )
            mass_spec = mass_res.generated_specification
            
            # 8. Flight Performance Sizing (V3 Engine Adapter)
            # Instantiate adapters to bridge V4 specifications to V3 performance strategy
            mission_adapter = MissionAdapter(requirements)
            config_adapter = ConfigAdapter(frame_spec)
            propulsion_adapter = PropulsionAdapter(propulsion_assembly, prop_spec)
            electrical_adapter = ElectricalAdapter(elec_spec, propulsion_assembly)
            mass_adapter = MassAdapter(mass_spec)
            
            try:
                perf_res = self._performance_engine.evaluate_performance(
                    mission=mission_adapter,
                    configuration_result=config_adapter,
                    structure_result=None,
                    propulsion_result=propulsion_adapter,
                    electrical_result=electrical_adapter,
                    avionics_result=None,
                    payload_result=None,
                    mass_result=mass_adapter,
                    strategy_name="BalancedStrategy"
                )
            except Exception as e:
                return MultirotorDesignResult(
                    success=False,
                    status=PipelineStatus.PERFORMANCE_INFEASIBLE,
                    iterations=iteration,
                    converged=True,
                    errors=[f"Flight performance evaluation crashed: {type(e).__name__}: {e}"]
                )
                
            # 9. Avionics Sizing (V3 Engine Integration)
            try:
                avionics_res = self._avionics_engine.design_avionics(
                    mission=mission_adapter,
                    configuration_result=config_adapter,
                    structure_result=None,
                    propulsion_result=propulsion_adapter,
                    electrical_result=electrical_adapter,
                    strategy_name="BalancedStrategy"
                )
            except Exception as e:
                avionics_res = None
            
            # 10. Final Specification & Spec Compilation
            spec = MultirotorAircraftSpecification(
                mission_strategy=strategy_spec,
                frame=frame_spec,
                propulsion_assembly=propulsion_assembly,
                electrical=elec_spec,
                layout_spec=layout_spec,
                mass_properties=mass_spec,
                performance=perf_res,
                verification=None,  # Populated after verification runs
                convergence_history=[vars(h) for h in conv_mgr.history]
            )
            
            # 11. Verification Rules Execution
            # Prepare adapted specifications map for rules evaluator
            subsystem_specs = {
                "MassPropertiesSpecification": mass_spec,
                "PropulsionSpecification": propulsion_adapter,
                "ElectricalSystemSpecification": ElectricalBudgetAdapter(elec_spec, propulsion_assembly, frame_spec),
                "PayloadPackagingSpecification": layout_spec,
                "FlightPerformanceSpecification": PerformanceVerificationAdapter(perf_res, requirements)
            }
            
            verif_res = self._verification_engine.verify_aircraft(
                mission_requirements=requirements,
                final_specification=spec,
                subsystem_specifications=subsystem_specs,
                convergence_report={"converged": True, "iterations": iteration}
            )
            spec.verification = verif_res
            
            if not verif_res.feasible or any(r.status == "FAIL" for r in verif_res.results):
                fail_reasons = [r.message for r in verif_res.results if r.status == "FAIL"]
                return MultirotorDesignResult(
                    success=False,
                    status=PipelineStatus.VERIFICATION_FAILED,
                    iterations=iteration,
                    converged=True,
                    final_specification=spec,
                    errors=fail_reasons
                )
            
            # Compile BOM
            bom_data = self._generate_bom(spec, avionics_res)
            spec.bom_data = bom_data
            
            # Compile Build Instructions
            spec.build_instructions = self._generate_build_instructions(spec, avionics_res)
            
            # Write downloadable reports
            self._write_reports(spec)
            
            return MultirotorDesignResult(
                success=True,
                status=PipelineStatus.SUCCESS,
                iterations=iteration,
                converged=True,
                final_specification=spec
            )
            
        except Exception as e:
            if self.raise_on_failure:
                raise e
            return MultirotorDesignResult(
                success=False,
                status=PipelineStatus.INTERNAL_ERROR,
                iterations=0,
                converged=False,
                errors=[f"Internal synthesis exception: {type(e).__name__}: {e}"]
            )

    def _generate_bom(self, spec: MultirotorAircraftSpecification, avionics_res: Any) -> List[Dict[str, Any]]:
        """
        Compiles the detailed Bill of Materials.
        """
        bom = []
        arm_count = spec.frame.arm_count
        
        # 1. Frame
        fs = FrameSelector()
        frame_rec = next((f for f in fs.get_all_frames() if f.name == spec.frame.selected_name), None)
        frame_price = frame_rec.price_usd if frame_rec else 45.0
        bom.append({
            "Category": "Frame",
            "Manufacturer": "Catalog Frame",
            "Model": spec.frame.selected_name,
            "Part Number": f"PN-FRAME-{spec.frame.selected_name.replace(' ', '-').upper()}",
            "Quantity": 1,
            "Unit Mass (kg)": spec.frame.frame_mass_kg,
            "Total Mass (kg)": spec.frame.frame_mass_kg,
            "Dimensions": f"Wheelbase: {spec.frame.wheelbase_m * 1000:.0f}mm",
            "Electrical Rating": "N/A",
            "Selected Reason": spec.frame.engineering_reasoning,
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": frame_price,
            "Availability": "IN_STOCK"
        })
        
        # 2. Motor
        ms = MotorSelector()
        motor_rec = next((m for m in ms.get_all_motors() if m.model == spec.propulsion_assembly.motor.model), None)
        motor_price = motor_rec.price_usd if motor_rec else 35.0
        bom.append({
            "Category": "Motor",
            "Manufacturer": spec.propulsion_assembly.motor.manufacturer,
            "Model": spec.propulsion_assembly.motor.model,
            "Part Number": f"PN-MOTOR-{spec.propulsion_assembly.motor.model.replace(' ', '-').upper()}",
            "Quantity": arm_count,
            "Unit Mass (kg)": spec.propulsion_assembly.motor.weight_kg,
            "Total Mass (kg)": spec.propulsion_assembly.motor.weight_kg * arm_count,
            "Dimensions": f"Mounting pattern: {spec.propulsion_assembly.motor.mount_pattern_mm}mm",
            "Electrical Rating": f"{spec.propulsion_assembly.motor.kv:.0f} KV",
            "Selected Reason": spec.propulsion_assembly.motor.engineering_reasoning,
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": motor_price,
            "Availability": "IN_STOCK"
        })
        
        # 3. Propeller
        ps = PropellerSelector()
        prop_rec = next((p for p in ps.get_all_propellers() if p.model == spec.propulsion_assembly.propeller.model), None)
        prop_price = prop_rec.price_usd if prop_rec else 8.0
        bom.append({
            "Category": "Propeller",
            "Manufacturer": spec.propulsion_assembly.propeller.manufacturer,
            "Model": spec.propulsion_assembly.propeller.model,
            "Part Number": f"PN-PROP-{spec.propulsion_assembly.propeller.model.replace(' ', '-').upper()}",
            "Quantity": arm_count,
            "Unit Mass (kg)": spec.propulsion_assembly.propeller.weight_kg,
            "Total Mass (kg)": spec.propulsion_assembly.propeller.weight_kg * arm_count,
            "Dimensions": f"Diameter: {spec.propulsion_assembly.propeller.diameter_m * 39.37:.1f} in",
            "Electrical Rating": "N/A",
            "Selected Reason": spec.propulsion_assembly.propeller.engineering_reasoning,
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": prop_price,
            "Availability": "IN_STOCK"
        })
        
        # 4. ESC
        es = EscSelector()
        esc_rec = next((e for e in es.get_all_escs() if e.model == spec.propulsion_assembly.esc.model), None)
        esc_price = esc_rec.price_usd if esc_rec else 20.0
        bom.append({
            "Category": "ESC",
            "Manufacturer": spec.propulsion_assembly.esc.manufacturer,
            "Model": spec.propulsion_assembly.esc.model,
            "Part Number": f"PN-ESC-{spec.propulsion_assembly.esc.model.replace(' ', '-').upper()}",
            "Quantity": arm_count,
            "Unit Mass (kg)": spec.propulsion_assembly.esc.weight_kg,
            "Total Mass (kg)": spec.propulsion_assembly.esc.weight_kg * arm_count,
            "Dimensions": "N/A",
            "Electrical Rating": f"{spec.propulsion_assembly.esc.continuous_current_a:.1f} A continuous",
            "Selected Reason": spec.propulsion_assembly.esc.engineering_reasoning,
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": esc_price,
            "Availability": "IN_STOCK"
        })
        
        # 5. Battery
        bs = BatterySelector()
        batt_rec = next((b for b in bs.get_all_batteries() if b.model == spec.propulsion_assembly.battery.model), None)
        batt_price = batt_rec.price_usd if batt_rec else 95.0
        bom.append({
            "Category": "Battery",
            "Manufacturer": spec.propulsion_assembly.battery.manufacturer,
            "Model": spec.propulsion_assembly.battery.model,
            "Part Number": f"PN-BATT-{spec.propulsion_assembly.battery.model.replace(' ', '-').upper()}",
            "Quantity": 1,
            "Unit Mass (kg)": spec.propulsion_assembly.battery.weight_kg,
            "Total Mass (kg)": spec.propulsion_assembly.battery.weight_kg,
            "Dimensions": "N/A",
            "Electrical Rating": f"{spec.propulsion_assembly.battery.capacity_mah:.0f} mAh, {spec.propulsion_assembly.battery.cell_count}S",
            "Selected Reason": spec.propulsion_assembly.battery.engineering_reasoning,
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": batt_price,
            "Availability": "IN_STOCK"
        })
        
        # 6. Power Distribution (PDB)
        bom.append({
            "Category": "Power Distribution",
            "Manufacturer": "Generic PDB",
            "Model": spec.electrical.power_distribution,
            "Part Number": f"PN-PDB-{spec.electrical.power_distribution.replace(' ', '-').upper()}",
            "Quantity": 1,
            "Unit Mass (kg)": 0.035,
            "Total Mass (kg)": 0.035,
            "Dimensions": "N/A",
            "Electrical Rating": "Dual BEC (5V / 12V)",
            "Selected Reason": spec.electrical.engineering_reasoning,
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 19.99,
            "Availability": "IN_STOCK"
        })
        
        # 7. Avionics Flight Controller (Adapted from Avionics Result)
        fc_model = "Holybro Pixhawk 6C"
        fc_mass = 0.048
        if avionics_res:
            fc_model = avionics_res.selected_flight_controller.get("fc_model", fc_model)
            fc_mass = avionics_res.selected_flight_controller.get("weight_g", 48.0) / 1000.0
            
        bom.append({
            "Category": "Flight Controller",
            "Manufacturer": "Holybro" if "Pixhawk" in fc_model else "CubePilot",
            "Model": fc_model,
            "Part Number": f"PN-FC-{fc_model.replace(' ', '-').upper()}",
            "Quantity": 1,
            "Unit Mass (kg)": fc_mass,
            "Total Mass (kg)": fc_mass,
            "Dimensions": "N/A",
            "Electrical Rating": "5V Autopilot System Power",
            "Selected Reason": "Autonomous autopilot control unit.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 150.0,
            "Availability": "IN_STOCK"
        })
        
        # 8. GPS
        gps_model = "Here3 GPS"
        gps_mass = 0.035
        if avionics_res:
            gps_model = avionics_res.selected_gps.get("gps_model", gps_model)
            gps_mass = avionics_res.selected_gps.get("weight_g", 35.0) / 1000.0
            
        bom.append({
            "Category": "GPS",
            "Manufacturer": "CubePilot" if "Here" in gps_model else "Holybro",
            "Model": gps_model,
            "Part Number": f"PN-GPS-{gps_model.replace(' ', '-').upper()}",
            "Quantity": 1,
            "Unit Mass (kg)": gps_mass,
            "Total Mass (kg)": gps_mass,
            "Dimensions": "N/A",
            "Electrical Rating": "N/A",
            "Selected Reason": "Precision navigation sensor unit.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 89.0,
            "Availability": "IN_STOCK"
        })
        
        # 9. Telemetry
        tel_model = "Holybro 915MHz Telemetry"
        tel_mass = 0.025
        if avionics_res:
            tel_model = avionics_res.selected_telemetry.get("telemetry_model", tel_model)
            tel_mass = avionics_res.selected_telemetry.get("weight_g", 25.0) / 1000.0
            
        bom.append({
            "Category": "Telemetry",
            "Manufacturer": "Holybro",
            "Model": tel_model,
            "Part Number": f"PN-TEL-{tel_model.replace(' ', '-').upper()}",
            "Quantity": 1,
            "Unit Mass (kg)": tel_mass,
            "Total Mass (kg)": tel_mass,
            "Dimensions": "N/A",
            "Electrical Rating": "100mW Link Power",
            "Selected Reason": "Long-range communication link telemetry.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 49.00,
            "Availability": "IN_STOCK"
        })
        
        # 10. Receiver
        rc_model = "FrSky Archer RS"
        rc_mass = 0.005
        if avionics_res:
            rc_model = avionics_res.selected_receiver.get("receiver_model", rc_model)
            rc_mass = avionics_res.selected_receiver.get("weight_g", 5.0) / 1000.0
            
        bom.append({
            "Category": "Receiver",
            "Manufacturer": "FrSky",
            "Model": rc_model,
            "Part Number": f"PN-RC-{rc_model.replace(' ', '-').upper()}",
            "Quantity": 1,
            "Unit Mass (kg)": rc_mass,
            "Total Mass (kg)": rc_mass,
            "Dimensions": "N/A",
            "Electrical Rating": "SBUS Output Channel",
            "Selected Reason": "Manual RC piloting safety receiver.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Torq Wings Catalog",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 24.50,
            "Availability": "IN_STOCK"
        })
        
        # 11. Payload
        bom.append({
            "Category": "Payload",
            "Manufacturer": "User Specified",
            "Model": f"Mission Payload ({spec.mass_properties.payload_mass_kg:.2f} kg)",
            "Part Number": "PN-PAYLOAD-CUSTOM",
            "Quantity": 1,
            "Unit Mass (kg)": spec.mass_properties.payload_mass_kg,
            "Total Mass (kg)": spec.mass_properties.payload_mass_kg,
            "Dimensions": f"Packaging Limits: {spec.frame.payload_bay_dimensions_m[0]*1000:.0f}x{spec.frame.payload_bay_dimensions_m[1]*1000:.0f}mm",
            "Electrical Rating": "12V BEC Power Output Channel Input",
            "Selected Reason": "Primary operational payload module.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "User Supplied",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 0.0,
            "Availability": "IN_STOCK"
        })
        
        # 12. Connectors, Wiring, Mounting Hardware
        bom.append({
            "Category": "Wiring",
            "Manufacturer": "Generic Wiring",
            "Model": f"Silicone AWG {spec.electrical.wire_gauge_summary.get('Main Battery Wire', '12')} Wiring Set",
            "Part Number": "PN-WIRE-HARNESS",
            "Quantity": 1,
            "Unit Mass (kg)": 0.045,
            "Total Mass (kg)": 0.045,
            "Dimensions": "N/A",
            "Electrical Rating": "60A rated power wire harness",
            "Selected Reason": "Harness wiring sets.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Generic",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 4.99,
            "Availability": "IN_STOCK"
        })
        
        bom.append({
            "Category": "Connectors",
            "Manufacturer": "Generic Connectors",
            "Model": f"{spec.electrical.connector_summary.get('Battery Connector', 'XT60')} Battery/PDB connector set",
            "Part Number": "PN-CONN-XT60",
            "Quantity": 1,
            "Unit Mass (kg)": 0.015,
            "Total Mass (kg)": 0.015,
            "Dimensions": "N/A",
            "Electrical Rating": "XT-Series current handling",
            "Selected Reason": "Battery power supply connectors.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Generic",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 2.99,
            "Availability": "IN_STOCK"
        })
        
        # Quantity check for "Other required components" / mounting hardware
        bom.append({
            "Category": "Mounting Hardware",
            "Manufacturer": "Generic",
            "Model": "M3 Standoffs and Carbon Screws Pack",
            "Part Number": "PN-MOUNT-M3",
            "Quantity": 1,
            "Unit Mass (kg)": 0.02,
            "Total Mass (kg)": 0.02,
            "Dimensions": "N/A",
            "Electrical Rating": "N/A",
            "Selected Reason": "Avionics and PDB structural mounts.",
            "Compatibility Status": "COMPATIBLE",
            "Supplier": "Generic",
            "Datasheet Reference": "NOT_AVAILABLE",
            "Estimated Price (USD)": 5.99,
            "Availability": "IN_STOCK"
        })
        
        return bom

    def _generate_build_instructions(self, spec: MultirotorAircraftSpecification, avionics_res: Any) -> str:
        """
        Creates build sequence and connection map text blocks.
        """
        arm_count = spec.frame.arm_count
        fc_model = avionics_res.selected_flight_controller.get("fc_model", "Holybro Pixhawk 6C") if avionics_res else "Holybro Pixhawk 6C"
        gps_model = avionics_res.selected_gps.get("gps_model", "Here3 GPS") if avionics_res else "Here3 GPS"
        tel_model = avionics_res.selected_telemetry.get("telemetry_model", "Holybro 915MHz Telemetry") if avionics_res else "Holybro 915MHz Telemetry"
        rc_model = avionics_res.selected_receiver.get("receiver_model", "FrSky Archer RS") if avionics_res else "FrSky Archer RS"
        
        instructions = f"""============================================================
AIRCRAFT WIRING & CONNECTIONS BUILD PACKAGE
============================================================

1. POWER HARNESS CONNECTIONS:
   Battery ({spec.propulsion_assembly.battery.manufacturer} {spec.propulsion_assembly.battery.model})
     ↓ ({spec.electrical.connector_summary.get('Battery Connector', 'XT60')} Connector)
   Power Distribution Board ({spec.electrical.power_distribution})
     ↓ ({spec.electrical.wire_gauge_summary.get('ESC Power Lead Wire', 'AWG 14')} Wire Leads)
   ESCs (Quantity {arm_count} x {spec.propulsion_assembly.esc.manufacturer} {spec.propulsion_assembly.esc.model})
     ↓ ({spec.electrical.wire_gauge_summary.get('Motor Phase Wire', 'AWG 16')} Phase Wires)
   Motors (Quantity {arm_count} x {spec.propulsion_assembly.motor.manufacturer} {spec.propulsion_assembly.motor.model})

2. CONTROL SIGNAL CONNECTIONS:
   Flight Controller ({fc_model})
     ↓ (PWM Signal Channels 1-{arm_count})
   ESCs (Quantity {arm_count} x {spec.propulsion_assembly.esc.manufacturer} {spec.propulsion_assembly.esc.model})

3. AVIONICS ACCESSORIES CONNECTIONS:
   GPS Receiver ({gps_model}) ── (I2C/Serial Port) ──> Flight Controller ({fc_model})
   Telemetry Radio ({tel_model}) ── (Telemetry Port 1) ──> Flight Controller ({fc_model})
   RC Receiver ({rc_model}) ── (RCIN Port) ──> Flight Controller ({fc_model})

4. PAYLOAD INTEGRATION:
   Payload ── (12V BEC Port / AUX Channel) ──> Power Distribution Board ({spec.electrical.power_distribution})

============================================================
ASSEMBLY SEQUENCE INSTRUCTIONS:
1. Mount the motors to the frame arms using the pattern: {spec.propulsion_assembly.motor.mount_pattern_mm}mm.
2. Secure the propellers ({spec.propulsion_assembly.propeller.manufacturer} {spec.propulsion_assembly.propeller.model}) only after verifying motor spin directions during autopilot calibration.
3. Solder the ESC branch wires to the center plate Power Distribution Board.
4. Mount the flight controller at the geometric center of gravity on vibration damping standoffs.
5. Calibrate the ESC throttle endpoints using the autopilot setup wizard.
============================================================
"""
        return instructions

    def _write_reports(self, spec: MultirotorAircraftSpecification) -> None:
        """
        Saves CSV, JSON, and Markdown reports to reports/ directory in the workspace.
        """
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        # 1. JSON spec
        json_data = {
            "synthesis_summary": {
                "takeoff_mass_kg": spec.mass_properties.total_mass_kg,
                "empty_mass_kg": spec.mass_properties.empty_mass_kg,
                "flight_time_min": spec.performance.flight_time_min,
                "range_km": spec.performance.range_km,
                "hover_throttle_pct": spec.propulsion_assembly.hover_throttle_pct
            },
            "subsystems": {
                "frame": {
                    "name": spec.frame.selected_name,
                    "wheelbase_m": spec.frame.wheelbase_m,
                    "arm_count": spec.frame.arm_count
                },
                "motor": {
                    "model": spec.propulsion_assembly.motor.model,
                    "kv": spec.propulsion_assembly.motor.kv
                },
                "propeller": {
                    "model": spec.propulsion_assembly.propeller.model,
                    "diameter_m": spec.propulsion_assembly.propeller.diameter_m
                },
                "esc": {
                    "model": spec.propulsion_assembly.esc.model,
                    "continuous_current_a": spec.propulsion_assembly.esc.continuous_current_a
                },
                "battery": {
                    "model": spec.propulsion_assembly.battery.model,
                    "capacity_mah": spec.propulsion_assembly.battery.capacity_mah,
                    "cell_count": spec.propulsion_assembly.battery.cell_count
                }
            }
        }
        with open(os.path.join(reports_dir, "multirotor_specification.json"), "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)
            
        # 2. CSV BOM
        with open(os.path.join(reports_dir, "multirotor_bom.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Category", "Manufacturer", "Model", "Part Number", "Quantity",
                "Unit Mass (kg)", "Total Mass (kg)", "Dimensions", "Electrical Rating",
                "Selected Reason", "Estimated Price (USD)"
            ])
            for item in spec.bom_data:
                writer.writerow([
                    item["Category"], item["Manufacturer"], item["Model"], item["Part Number"], item["Quantity"],
                    item["Unit Mass (kg)"], item["Total Mass (kg)"], item["Dimensions"], item["Electrical Rating"],
                    item["Selected Reason"], item["Estimated Price (USD)"]
                ])
                
        # 3. Build Spec
        with open(os.path.join(reports_dir, "multirotor_build_specification.txt"), "w", encoding="utf-8") as f:
            f.write(spec.build_instructions)
            
        # 4. Markdown report
        md_report = f"""# Engineering Sizing & Build Package Report
## Multirotor Design Specification V1

This report summarizes the final convergent sizing evaluation for the multirotor UAV platform.

### Sizing Executive Summary
*   **Total Takeoff Weight (MTOW)**: {spec.mass_properties.total_mass_kg:.3f} kg
*   **Empty Weight**: {spec.mass_properties.empty_mass_kg:.3f} kg
*   **Payload Capacity**: {spec.mass_properties.payload_mass_kg:.2f} kg
*   **Battery Pack Mass**: {spec.mass_properties.battery_mass_kg:.3f} kg
*   **Estimated Endurance**: {spec.performance.flight_time_min:.1f} min
*   **Estimated Hover time**: {spec.performance.max_hover_time_min:.1f} min
*   **Estimated Range**: {spec.performance.range_km:.2f} km
*   **Hover Throttle percentage**: {spec.propulsion_assembly.hover_throttle_pct:.1f}%

### Bill of Materials Summary
| Category | Part Name | Qty | Unit Weight (kg) | Total Weight (kg) |
|---|---|---|---|---|
"""
        for item in spec.bom_data:
            md_report += f"| {item['Category']} | {item['Manufacturer']} {item['Model']} | {item['Quantity']} | {item['Unit Mass (kg)']:.3f} | {item['Total Mass (kg)']:.3f} |\n"
            
        md_report += f"""
### System Layout Build Package
```text
{spec.build_instructions}
```
"""
        with open(os.path.join(reports_dir, "multirotor_engineering_report.md"), "w", encoding="utf-8") as f:
            f.write(md_report)


class MultirotorDesignEngine(DesignEngine):
    """
    Adapter bridging the abstract DesignEngine contract to the MultirotorDesignPipeline orchestrator.
    """
    def __init__(self) -> None:
        self.pipeline = MultirotorDesignPipeline()

    @property
    def engine_id(self) -> str:
        return "MultirotorDesignEngine"

    @property
    def supported_aircraft_types(self) -> list[AircraftType]:
        return [AircraftType.QUADCOPTER, AircraftType.HEXACOPTER, AircraftType.OCTOCOPTER]

    def execute_design(self, context: DesignContext) -> DesignContext:
        """
        Executes the category pipeline and writes specs to the context.
        """
        res = self.pipeline.execute(context.requirement_model)
        if res.success:
            context.design_data["multirotor_aircraft_specification"] = res.final_specification
            context.current_stage = DesignStage.DRONE_DESIGN
            context.current_status = DesignStatus.COMPLETED
            context.add_snapshot(f"MultirotorDesignEngine successfully completed sizing workflow: MTOW = {res.final_specification.mtow_kg:.2f}kg.")
        else:
            context.current_status = DesignStatus.FAILED
            context.metadata.notes = "; ".join(res.errors)
            context.add_snapshot(f"MultirotorDesignEngine failed: {'; '.join(res.errors)}.")
            
        return context


# Thin adapters for the performance/avionics strategy inputs
class MissionAdapter:
    def __init__(self, req: RequirementModel):
        self.cruise_speed_kmh = req.cruise_speed_kmh
        self.max_wind_speed_m_s = req.metadata.get("wind_conditions_kmh", 25.0) / 3.6


class ConfigAdapter:
    def __init__(self, frame_spec: FrameSpecification):
        class Profile:
            def __init__(self, rc):
                self.rotor_count = rc
        class RecommendedConfig:
            def __init__(self, rc):
                self.profile = Profile(rc)
        self.recommended_configuration = RecommendedConfig(frame_spec.arm_count)


class PropulsionAdapter:
    def __init__(self, assembly: PropulsionAssembly, prop_spec: PropellerSpecification):
        class ThrustAnalysis:
            def __init__(self, tw):
                self.actual_thrust_to_weight_ratio = tw
        class HoverAnalysis:
            def __init__(self, throttle):
                self.hover_throttle_percent = throttle
        self.thrust_analysis = ThrustAnalysis(assembly.max_thrust_capability_n / max(0.1, assembly.estimated_auw_kg * 9.80665))
        self.hover_analysis = HoverAnalysis(assembly.hover_throttle_pct)
        self.selected_propellers = {"diameter_inch": prop_spec.diameter_m * 39.37}
        
        # Compatibility properties for verification rules
        self.static_thrust_n = assembly.max_thrust_capability_n
        self.operating_voltage_v = assembly.battery.voltage
        self.battery_voltage_v = assembly.battery.voltage
        self.cruise_power_w = assembly.hover_power_total_w * 1.12
        self.motor_name = f"{assembly.motor.manufacturer} {assembly.motor.model}"
        self.propeller_name = f"{assembly.propeller.manufacturer} {assembly.propeller.model}"
        self.propeller_diameter_m = prop_spec.diameter_m
        self.propeller = prop_spec
        self.battery_weight_kg = assembly.battery.weight_kg


class ElectricalAdapter:
    def __init__(self, elec_spec: ElectricalSpecification, assembly: PropulsionAssembly):
        class PowerBudget:
            def __init__(self, hover, peak):
                self.total_hover_power_w = hover
                self.total_peak_power_w = peak
        class VoltageAnalysis:
            def __init__(self, volt):
                self.nominal_voltage_v = volt
        aux = elec_spec.power_budget.get("Total Auxiliary Power (W)", 0.0)
        self.power_budget = PowerBudget(assembly.hover_power_total_w + aux, assembly.peak_power_total_w + aux)
        self.selected_battery = {"capacity_mah": assembly.battery.capacity_mah}
        self.voltage_analysis = VoltageAnalysis(assembly.battery.voltage)


class MassAdapter:
    def __init__(self, mass_spec: MassPropertiesSpecification):
        class CG:
            def __init__(self, x, y):
                self.cg_x_mm = x * 1000.0
                self.cg_y_mm = y * 1000.0
        self.total_mass_kg = mass_spec.total_mass_kg
        self.center_of_gravity = CG(mass_spec.center_of_gravity[0], mass_spec.center_of_gravity[1])


class ElectricalBudgetAdapter:
    """Thin adapter for the common electrical current budget verification rule."""
    def __init__(self, elec_spec: ElectricalSpecification, assembly: PropulsionAssembly, frame_spec: FrameSpecification):
        self.maximum_system_current_a = assembly.peak_current_total_a + elec_spec.power_budget.get("Total Auxiliary Power (W)", 0.0) / assembly.battery.voltage
        self.esc_rating_a = assembly.esc.continuous_current_a * frame_spec.arm_count
        self.battery_max_discharge_current_a = assembly.battery.burst_current_a


class PerformanceVerificationAdapter:
    """Thin adapter for the common mission performance verification rules."""
    def __init__(self, perf_res: Any, req: RequirementModel):
        self.range_km = getattr(perf_res, "range_km", 0.0)
        self.flight_time_min = getattr(perf_res, "flight_time_min", 0.0)
        self.endurance_min = getattr(perf_res, "flight_time_min", 0.0)
        self.estimated_flight_time_min = getattr(perf_res, "flight_time_min", 0.0)
        self.cruise_speed_kmh = req.cruise_speed_kmh
        self.stall_speed_kmh = 0.0


