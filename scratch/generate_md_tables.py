import sys
import os

sys.path.append(r"c:\Users\acer\Documents\torqwings studio v2")

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.pipeline.pipeline_context import FixedWingPipelineContext
from backend.design.fixed_wing.pipeline.pipeline_result import FixedWingDesignResult, PipelineStatus

# Custom executor to collect iteration records
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

pipeline = FixedWingDesignPipeline(tolerance=0.01, max_iterations=30)

# We'll run the sizing loop step-by-step to capture every subsystem variable
context = FixedWingPipelineContext(requirements=req)
pipeline._req_validator.validate(req)
mission_reqs = pipeline._translate_requirements(req)
context.mission_result = pipeline._mission_engine.process_mission(mission_reqs)

from backend.design.fixed_wing.configuration.configuration_requirements import ConfigurationRequirements
config_reqs = ConfigurationRequirements(mission_result=context.mission_result)
context.configuration_result = pipeline._configuration_engine.process_configuration(config_reqs)

initial_mtow = max(1.5, req.payload_weight_kg * 2.5)
context.current_mtow = initial_mtow
frozen_config = context.configuration_result

# Import subsystem requirements
from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements
from backend.design.fixed_wing.tail.tail_requirements import TailRequirements
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements
from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements
from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements

iteration = 0
converged = False

rows = []

while iteration < 30 and not converged:
    iteration += 1
    old_mtow = context.current_mtow
    context.previous_mtow = old_mtow
    
    context.mission_result.mission_profile.maximum_takeoff_weight_limit_kg = old_mtow
    context.mission_result.constraints.maximum_takeoff_weight_kg = req.maximum_takeoff_weight_kg or 25.0
    
    wing_reqs = WingRequirements(mission_result=context.mission_result, configuration_result=frozen_config)
    context.wing_result = pipeline._wing_engine.process_wing_design(wing_reqs)
    
    airfoil_reqs = AirfoilRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result)
    context.airfoil_result = pipeline._airfoil_engine.process_airfoil_design(airfoil_reqs)
    
    tail_reqs = TailRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result)
    context.tail_result = pipeline._tail_engine.process_tail_design(tail_reqs)
    
    fuselage_reqs = FuselageRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result)
    context.fuselage_result = pipeline._fuselage_engine.process_fuselage_design(fuselage_reqs)
    
    propulsion_reqs = PropulsionRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result)
    context.propulsion_result = pipeline._propulsion_engine.process_propulsion_design(propulsion_reqs)
    
    avionics_reqs = AvionicsRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result)
    context.avionics_result = pipeline._avionics_engine.process_avionics_design(avionics_reqs)
    
    payload_reqs = PayloadRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result, avionics_result=context.avionics_result)
    context.payload_result = pipeline._payload_engine.process_payload_design(payload_reqs)
    
    mass_reqs = MassRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result, avionics_result=context.avionics_result, payload_result=context.payload_result)
    context.mass_properties_result = pipeline._mass_properties_engine.process_mass_design(mass_reqs)
    
    flight_reqs = FlightRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=context.wing_result, airfoil_result=context.airfoil_result, tail_result=context.tail_result, fuselage_result=context.fuselage_result, propulsion_result=context.propulsion_result, avionics_result=context.avionics_result, payload_result=context.payload_result, mass_result=context.mass_properties_result)
    context.performance_result = pipeline._flight_performance_engine.process_performance_design(flight_reqs)
    
    wb = context.mass_properties_result.weight_breakdown
    geom = context.wing_result.wing_geometry
    f_geom = context.fuselage_result.fuselage_geometry
    
    raw_new_mtow = round(wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg, 4)
    relaxed_mtow = round(0.75 * raw_new_mtow + 0.25 * old_mtow, 4)
    
    wing_mass = round(geom.reference_area_m2 * 2.8, 4)
    h_mass = round(context.tail_result.horizontal_tail.area_m2 * 2.2, 4)
    v_mass = round(context.tail_result.vertical_tail.area_m2 * 2.2, 4)
    tail_mass = round(h_mass + v_mass, 4)
    fuse_mass = round(f_geom.length_m * 1.35, 4)
    struct_mass = wb.structural_weight_kg
    
    motor_g = context.propulsion_result.power_analysis.metadata.get("motor_weight_g", 310)
    motor_mass = round(motor_g / 1000.0, 4)
    prop_mass = 0.065
    esc_mass = 0.0  # not in components separately
    propulsion_mass = wb.propulsion_weight_kg
    
    battery_mass = wb.battery_fuel_weight_kg
    avionics_mass = wb.avionics_weight_kg
    payload_mass = wb.payload_weight_kg
    useful_load = wb.useful_load_kg
    
    step_record = pipeline._evaluator.evaluate_step(iteration, old_mtow, relaxed_mtow)
    context.convergence_history.append(step_record)
    converged = step_record.converged
    
    rows.append((
        iteration, old_mtow, wing_mass, fuse_mass, tail_mass, struct_mass,
        motor_mass, prop_mass, esc_mass, propulsion_mass, battery_mass,
        avionics_mass, payload_mass, 0.0, raw_new_mtow, relaxed_mtow, step_record.relative_delta
    ))
    
    context.current_mtow = relaxed_mtow

# Format Markdown Table for MTOW Trace
print("| Iter | Input MTOW (kg) | Wing Mass (kg) | Fuse Mass (kg) | Tail Mass (kg) | Struct Mass (kg) | Motor Mass (kg) | Prop Mass (kg) | ESC Mass (kg) | Prop Mass (kg) | Batt Mass (kg) | Avionics Mass (kg) | Payload Mass (kg) | Raw MTOW (kg) | Relaxed MTOW (kg) | Rel Delta (%) |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r[0]} | {r[1]:.4f} | {r[2]:.4f} | {r[3]:.4f} | {r[4]:.4f} | {r[5]:.4f} | {r[6]:.4f} | {r[7]:.4f} | {r[8]:.4f} | {r[9]:.4f} | {r[10]:.4f} | {r[11]:.4f} | {r[12]:.4f} | {r[14]:.4f} | {r[15]:.4f} | {r[16]*100:.4f}% |")

# Wing Sizing table
print("\n--- WING SIZING TABLE ---")
print("| Iter | MTOW (kg) | Wing Loading (kg/m²) | Target Stall (km/h) | CLmax | Air Density (kg/m³) | Wing Area (m²) | Aspect Ratio | Span (m) | Root Chord (m) | Tip Chord (m) | MAC (m) |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
context.current_mtow = initial_mtow
iteration = 0
converged = False
while iteration < 30 and not converged:
    iteration += 1
    old_mtow = context.current_mtow
    context.mission_result.mission_profile.maximum_takeoff_weight_limit_kg = old_mtow
    
    wing_reqs = WingRequirements(mission_result=context.mission_result, configuration_result=frozen_config)
    wing_res = pipeline._wing_engine.process_wing_design(wing_reqs)
    geom = wing_res.wing_geometry
    
    # We execute airfoil to get actual CLmax
    airfoil_reqs = AirfoilRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res)
    airfoil_res = pipeline._airfoil_engine.process_airfoil_design(airfoil_reqs)
    cl_max = airfoil_res.polar_data.max_lift_coeff
    
    # Run the rest of the loop to keep current_mtow correct
    tail_reqs = TailRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res, airfoil_result=airfoil_res)
    tail_res = pipeline._tail_engine.process_tail_design(tail_reqs)
    fuselage_reqs = FuselageRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res, airfoil_result=airfoil_res, tail_result=tail_res)
    fuselage_res = pipeline._fuselage_engine.process_fuselage_design(fuselage_reqs)
    propulsion_reqs = PropulsionRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res, airfoil_result=airfoil_res, tail_result=tail_res, fuselage_result=fuselage_res)
    propulsion_res = pipeline._propulsion_engine.process_propulsion_design(propulsion_reqs)
    avionics_reqs = AvionicsRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res, airfoil_result=airfoil_res, tail_result=tail_res, fuselage_result=fuselage_res, propulsion_result=propulsion_res)
    avionics_res = pipeline._avionics_engine.process_avionics_design(avionics_reqs)
    payload_reqs = PayloadRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res, airfoil_result=airfoil_res, tail_result=tail_res, fuselage_result=fuselage_res, propulsion_result=propulsion_res, avionics_result=avionics_res)
    payload_res = pipeline._payload_engine.process_payload_design(payload_reqs)
    mass_reqs = MassRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res, airfoil_result=airfoil_res, tail_result=tail_res, fuselage_result=fuselage_res, propulsion_result=propulsion_res, avionics_result=avionics_res, payload_result=payload_res)
    mass_res = pipeline._mass_properties_engine.process_mass_design(mass_reqs)
    flight_reqs = FlightRequirements(mission_result=context.mission_result, configuration_result=frozen_config, wing_result=wing_res, airfoil_result=airfoil_res, tail_result=tail_res, fuselage_result=fuselage_res, propulsion_result=propulsion_res, avionics_result=avionics_res, payload_result=payload_res, mass_result=mass_res)
    flight_res = pipeline._flight_performance_engine.process_performance_design(flight_reqs)
    
    wb = mass_res.weight_breakdown
    raw_new_mtow = round(wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg + wb.useful_load_kg, 4)
    relaxed_mtow = round(0.75 * raw_new_mtow + 0.25 * old_mtow, 4)
    
    step_record = pipeline._evaluator.evaluate_step(iteration, old_mtow, relaxed_mtow)
    converged = step_record.converged
    
    print(f"| {iteration} | {old_mtow:.4f} | {geom.wing_loading_kg_m2:.4f} | {context.mission_result.mission_profile.stall_speed_target_kmh:.1f} | {1.4:.1f} | {context.mission_result.mission_profile.air_density_kg_m3:.4f} | {geom.reference_area_m2:.4f} | {geom.aspect_ratio:.2f} | {geom.span_m:.4f} | {geom.root_chord_m:.4f} | {geom.tip_chord_m:.4f} | {geom.mean_aerodynamic_chord_m:.4f} |")
    
    context.current_mtow = relaxed_mtow
