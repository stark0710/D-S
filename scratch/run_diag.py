import sys
import os

# Add workspace root to path
sys.path.append(r"c:\Users\acer\Documents\torqwings studio v2")

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.pipeline.pipeline_result import FixedWingDesignResult, PipelineStatus
from backend.design.fixed_wing.pipeline.convergence import ConvergenceEvaluator

# Subclass pipeline or write a custom run script to print details of each iteration
class ForensicPipeline(FixedWingDesignPipeline):
    def execute(self, requirements: RequirementModel) -> FixedWingDesignResult:
        context = FixedWingPipelineContext(requirements=requirements)
        
        # 1. Validate (skip details, assume valid)
        self._req_validator.validate(requirements)
        
        # 2. Mission Requirements
        mission_reqs = self._translate_requirements(requirements)
        context.mission_result = self._mission_engine.process_mission(mission_reqs)
        
        # 3. Configuration (freeze)
        config_reqs = ConfigurationRequirements = type('ConfigurationRequirements', (object,), {})()
        from backend.design.fixed_wing.configuration.configuration_requirements import ConfigurationRequirements
        config_reqs = ConfigurationRequirements(mission_result=context.mission_result)
        context.configuration_result = self._configuration_engine.process_configuration(config_reqs)
        
        # 4. Establish initial MTOW
        initial_mtow = requirements.maximum_takeoff_weight_kg
        if initial_mtow is None or initial_mtow <= 0.0:
            initial_mtow = max(1.5, requirements.payload_weight_kg * 2.5)
        
        context.current_mtow = initial_mtow
        frozen_config = context.configuration_result
        
        print(f"=== INITIAL EST MTOW: {initial_mtow} kg ===")
        print("Starting Sizing Loop...\n")
        
        iteration = 0
        converged = False
        
        # We import requirements classes
        from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
        from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements
        from backend.design.fixed_wing.tail.tail_requirements import TailRequirements
        from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements
        from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
        from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements
        from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements
        from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
        from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
        from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements
        
        while iteration < self.max_iterations and not converged:
            iteration += 1
            old_mtow = context.current_mtow
            context.previous_mtow = old_mtow
            
            context.mission_result.mission_profile.maximum_takeoff_weight_limit_kg = old_mtow
            context.mission_result.constraints.maximum_takeoff_weight_kg = requirements.maximum_takeoff_weight_kg or 25.0
            
            # Execute subsystems
            wing_reqs = WingRequirements(mission_result=context.mission_result, configuration_result=frozen_config)
            context.wing_result = self._wing_engine.process_wing_design(wing_reqs)
            
            airfoil_reqs = AirfoilRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result)
            context.airfoil_result = self._airfoil_engine.process_airfoil_design(airfoil_reqs)
            
            tail_reqs = TailRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result)
            context.tail_result = self._tail_engine.process_tail_design(tail_reqs)
            
            fuselage_reqs = FuselageRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result)
            context.fuselage_result = self._fuselage_engine.process_fuselage_design(fuselage_reqs)
            
            propulsion_reqs = PropulsionRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result)
            context.propulsion_result = self._propulsion_engine.process_propulsion_design(propulsion_reqs)
            
            avionics_reqs = AvionicsRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result)
            context.avionics_result = self._avionics_engine.process_avionics_design(avionics_reqs)
            
            payload_reqs = PayloadRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result, avionics_result=context.avionics_result)
            context.payload_result = self._payload_engine.process_payload_design(payload_reqs)
            
            mass_reqs = MassRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result, avionics_result=context.avionics_result, payload_result=context.payload_result)
            context.mass_properties_result = self._mass_properties_engine.process_mass_design(mass_reqs)
            
            flight_reqs = FlightRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result, avionics_result=context.avionics_result, payload_result=context.payload_result, mass_result=context.mass_properties_result)
            context.performance_result = self._flight_performance_engine.process_performance_design(flight_reqs)
            
            # Print detailed iteration results
            geom = context.wing_result.wing_geometry
            f_geom = context.fuselage_result.fuselage_geometry
            wb = context.mass_properties_result.weight_breakdown
            raw_new_mtow = round(wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg, 4)
            relaxed_mtow = round(0.75 * raw_new_mtow + 0.25 * old_mtow, 4)
            
            # Extract structures
            wing_mass = round(geom.reference_area_m2 * 2.8, 4)
            h_mass = round(context.tail_result.horizontal_tail.area_m2 * 2.2, 4)
            v_mass = round(context.tail_result.vertical_tail.area_m2 * 2.2, 4)
            tail_mass = round(h_mass + v_mass, 4)
            fuse_mass = round(f_geom.length_m * 1.35, 4)
            struct_mass = wb.structural_weight_kg
            
            # Extract propulsion components
            motor_g = context.propulsion_result.power_analysis.metadata.get("motor_weight_g", 310)
            motor_mass = round(motor_g / 1000.0, 4)
            prop_mass = 0.065
            esc_mass = 0.0  # ESC mass is not explicitly stored separately in ComponentMass or breakdown, let's verify if there is any other
            propulsion_mass = wb.propulsion_weight_kg
            
            battery_mass = wb.battery_fuel_weight_kg
            avionics_mass = wb.avionics_weight_kg
            payload_mass = wb.payload_weight_kg
            useful_load = wb.useful_load_kg
            
            step_record = self._evaluator.evaluate_step(iteration, old_mtow, relaxed_mtow)
            context.convergence_history.append(step_record)
            converged = step_record.converged
            
            print(f"--- Iteration {iteration} ---")
            print(f"  Input MTOW: {old_mtow:.4f} kg")
            print(f"  Wing Area: {geom.reference_area_m2:.4f} m2, Span: {geom.span_m:.4f} m, MAC: {geom.mean_aerodynamic_chord_m:.4f} m")
            print(f"  Fuselage Length: {f_geom.length_m:.4f} m")
            print(f"  Component Breakdown:")
            print(f"    Wing mass: {wing_mass:.4f} kg")
            print(f"    Fuselage mass: {fuse_mass:.4f} kg")
            print(f"    Tail mass: {tail_mass:.4f} kg (H: {h_mass:.4f}, V: {v_mass:.4f})")
            print(f"    Total Structure mass: {struct_mass:.4f} kg (Sum wing+fuse+tail = {wing_mass+fuse_mass+tail_mass:.4f})")
            print(f"    Motor mass: {motor_mass:.4f} kg, Prop mass: {prop_mass:.4f} kg")
            print(f"    Total Propulsion mass: {propulsion_mass:.4f} kg")
            print(f"    Battery mass: {battery_mass:.4f} kg")
            print(f"    Avionics mass: {avionics_mass:.4f} kg")
            print(f"    Payload mass: {payload_mass:.4f} kg")
            print(f"    Useful load: {useful_load:.4f} kg")
            print(f"    Raw calculated MTOW: {raw_new_mtow:.4f} kg")
            print(f"    Under-relaxed MTOW: {relaxed_mtow:.4f} kg")
            print(f"    Relative delta: {step_record.relative_delta*100:.4f}%")
            print(f"    Static Margin: {context.mass_properties_result.static_margin*100:.2f}%")
            print()
            
            context.current_mtow = relaxed_mtow
            
        # Post-Convergence Verification
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
        
        return self._build_result(context, PipelineStatus.SUCCESS, converged, iteration)

# Set up test requirement
req = RequirementModel(
    mission_type=MissionType.MAPPING,
    payload_weight_kg=2.0,
    target_flight_time_min=90.0,
    target_range_km=60.0,
    cruise_speed_kmh=95.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
)

pipeline = ForensicPipeline(tolerance=0.01, max_iterations=30)
res = pipeline.execute(req)

print("=== FINAL CONVERGED RESULTS ===")
print(f"Success: {res.success}")
print(f"Status: {res.status}")
print(f"Iterations: {res.iterations}")
print(f"Converged: {res.converged}")
if res.success:
    wb = res.mass_properties_result.weight_breakdown
    print(f"MTOW: {wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg:.4f} kg")
    print(f"Wing area: {res.wing_result.wing_geometry.reference_area_m2:.4f} m2")
    print(f"Wing span: {res.wing_result.wing_geometry.span_m:.4f} m")
    print(f"Fuselage length: {res.fuselage_result.fuselage_geometry.length_m:.4f} m")
    print(f"Static margin: {res.mass_properties_result.static_margin*100:.2f}%")
    print(f"Verification result: {res.verification_result.compliance_report.overall_compliance if hasattr(res.verification_result, 'compliance_report') else 'No compliance_report'}")
    
    # Detail component locations and moments for CG
    print("\n=== COMPONENT MOMENTS TABLE ===")
    print(f"{'Component':<20} | {'Mass (kg)':<10} | {'X (m)':<8} | {'Moment (kg*m)':<12}")
    print("-" * 60)
    total_moment = 0.0
    total_mass = 0.0
    for c in res.mass_properties_result.component_masses:
        mom = c.mass_kg * c.x_m
        total_moment += mom
        total_mass += c.mass_kg
        print(f"{c.name:<20} | {c.mass_kg:<10.4f} | {c.x_m:<8.4f} | {mom:<12.4f}")
    print("-" * 60)
    print(f"{'SUM':<20} | {total_mass:<10.4f} | {total_moment/total_mass:<8.4f} | {total_moment:<12.4f}")
    
    # Neutral Point and Static Margin math details
    w_geom = res.wing_result.wing_geometry
    f_geom = res.fuselage_result.fuselage_geometry
    mac = w_geom.mean_aerodynamic_chord_m
    wing_x = getattr(f_geom, 'wing_attachment_x_m', 0.0)
    quarter_chord_x = w_geom.quarter_chord_x_m
    global_quarter_chord = wing_x + quarter_chord_x
    print(f"\n=== CG & NEUTRAL POINT ANALYSIS ===")
    print(f"Fuselage Length: {f_geom.length_m} m")
    print(f"Wing Attachment X (wing_x): {wing_x} m")
    print(f"Wing root leading edge X: {wing_x} m")
    print(f"Wing quarter-chord relative to root LE: {quarter_chord_x:.4f} m")
    print(f"Wing global quarter-chord: {global_quarter_chord:.4f} m")
    print(f"Wing MAC: {mac:.4f} m")
    
    # Let's print out what StabilityMarginCalculator did
    cg_x = res.mass_properties_result.center_of_gravity[0]
    np_pct = 0.42 # Since horizontal tail exists and is Conventional
    neutral_point_x = global_quarter_chord + (np_pct * mac)
    calc_sm = (neutral_point_x - cg_x) / mac
    print(f"Calculated CG X: {cg_x:.4f} m")
    print(f"Neutral Point X: {neutral_point_x:.4f} m (np_pct = {np_pct})")
    print(f"Neutral Point % MAC (global): {(neutral_point_x - wing_x) / mac * 100:.2f}%")
    print(f"CG % MAC (global): {(cg_x - wing_x) / mac * 100:.2f}%")
    print(f"Static Margin (fraction): {calc_sm:.4f} ({calc_sm*100:.2f}%)")
