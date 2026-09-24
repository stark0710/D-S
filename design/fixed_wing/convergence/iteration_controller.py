"""
Fixed-Wing Iteration Controller
"""

from typing import Dict, Any
from backend.design.common.optimization.optimization_context import OptimizationContext

from backend.design.fixed_wing.wing.optimization.wing_planform_optimizer import WingPlanformOptimizer
from backend.design.fixed_wing.fuselage.optimization.fuselage_optimizer import FuselageOptimizer
from backend.design.fixed_wing.payload.optimization.payload_optimizer import PayloadPackagingOptimizer
from backend.design.fixed_wing.tail.optimization.tail_optimizer import TailOptimizer
from backend.design.fixed_wing.propulsion.optimization.propulsion_optimizer import PropulsionOptimizer
from backend.design.fixed_wing.electrical.electrical_optimizer import ElectricalOptimizer
from backend.design.fixed_wing.mass_properties.optimization.mass_optimizer import MassPropertiesOptimizer
from backend.design.fixed_wing.cg.optimization.cg_optimizer import CGOptimizer
from backend.design.fixed_wing.performance.optimization.performance_engine import FlightPerformanceOptimizer


class IterationController:
    """
    Coordinates execution of all 9 subsystem optimizers in sequence,
    updating specifications in the OptimizationContext.
    """
    def __init__(self) -> None:
        self.wing_opt = WingPlanformOptimizer()
        self.fuse_opt = FuselageOptimizer()
        self.payload_opt = PayloadPackagingOptimizer()
        self.tail_opt = TailOptimizer()
        self.prop_opt = PropulsionOptimizer()
        self.elec_opt = ElectricalOptimizer()
        self.mass_opt = MassPropertiesOptimizer()
        self.cg_opt = CGOptimizer()
        self.perf_opt = FlightPerformanceOptimizer()

    def run_iteration(self, context: OptimizationContext) -> Dict[str, Any]:
        """Runs one full design iteration pass through all subsystems."""
        # 1. Wing
        wing_res = self.wing_opt.optimize(context)
        if not wing_res.success:
            raise RuntimeError(f"WingPlanformOptimizer failed: {wing_res.message}")
        context.previous_specifications["WingPlanformSpecification"] = wing_res.generated_specification
        context.previous_specifications["WingPlanformOptimizer"] = wing_res.generated_specification
        if hasattr(context.requirements, "wing_result") and wing_res.winning_candidate:
            geom_result = wing_res.winning_candidate.derived_variables.get("wing_result")
            if geom_result:
                context.requirements.wing_result = geom_result

        # 2. Fuselage
        fuse_res = self.fuse_opt.optimize(context)
        if not fuse_res.success:
            raise RuntimeError(f"FuselageOptimizer failed: {fuse_res.message}")
        context.previous_specifications["FuselageSpecification"] = fuse_res.generated_specification
        context.previous_specifications["FuselageOptimizer"] = fuse_res.generated_specification
        if hasattr(context.requirements, "fuselage_result") and fuse_res.winning_candidate:
            geom_result = fuse_res.winning_candidate.derived_variables.get("fuselage_result")
            if geom_result:
                context.requirements.fuselage_result = geom_result

        # 3. Payload Packaging
        payload_res = self.payload_opt.optimize(context)
        if not payload_res.success:
            raise RuntimeError(f"PayloadPackagingOptimizer failed: {payload_res.message}")
        context.previous_specifications["PayloadPackagingSpecification"] = payload_res.generated_specification
        context.previous_specifications["PayloadPackagingOptimizer"] = payload_res.generated_specification
        if hasattr(context.requirements, "payload_result") and payload_res.winning_candidate:
            geom_result = payload_res.winning_candidate.derived_variables.get("payload_result")
            if geom_result:
                context.requirements.payload_result = geom_result
            elif context.requirements.payload_result:
                pay_layout = getattr(context.requirements.payload_result, "payload_layout", None)
                f_geom = getattr(getattr(context.requirements, "fuselage_result", None), "fuselage_geometry", None)
                if f_geom and pay_layout:
                    pay_layout.compartment_length_m = f_geom.payload_bay_length_m
                    pay_layout.compartment_width_m = f_geom.payload_bay_width_m
                    pay_layout.compartment_height_m = f_geom.payload_bay_height_m
                    pay_pos = payload_res.winning_candidate.derived_variables.get("payload_position")
                    if pay_pos is not None:
                        pay_layout.placement_x_m = pay_pos

        # 4. Tail
        tail_res = self.tail_opt.optimize(context)
        if not tail_res.success:
            raise RuntimeError(f"TailOptimizer failed: {tail_res.message}")
        context.previous_specifications["TailSpecification"] = tail_res.generated_specification
        context.previous_specifications["TailOptimizer"] = tail_res.generated_specification
        if hasattr(context.requirements, "tail_result") and tail_res.winning_candidate:
            geom_result = tail_res.winning_candidate.derived_variables.get("tail_result")
            if geom_result:
                context.requirements.tail_result = geom_result


        # 5. Propulsion
        prop_res = self.prop_opt.optimize(context)
        if not prop_res.success:
            raise RuntimeError(f"PropulsionOptimizer failed: {prop_res.message}")


        context.previous_specifications["PropulsionSpecification"] = prop_res.generated_specification
        context.previous_specifications["PropulsionOptimizer"] = prop_res.generated_specification
        if hasattr(context.requirements, "propulsion_result") and prop_res.winning_candidate:
            geom_result = prop_res.winning_candidate.derived_variables.get("propulsion_result")
            if geom_result:
                context.requirements.propulsion_result = geom_result


        # 6. Electrical
        elec_res = self.elec_opt.optimize(context)
        if not elec_res.success:
            raise RuntimeError(f"ElectricalOptimizer failed: {elec_res.message}")
        context.previous_specifications["ElectricalSystemSpecification"] = elec_res.generated_specification
        context.previous_specifications["ElectricalOptimizer"] = elec_res.generated_specification

        # 7. Mass Properties
        mass_res = self.mass_opt.optimize(context)
        if not mass_res.success:
            raise RuntimeError(f"MassPropertiesOptimizer failed: {mass_res.message}")
        context.previous_specifications["MassPropertiesSpecification"] = mass_res.generated_specification
        context.previous_specifications["MassPropertiesOptimizer"] = mass_res.generated_specification
        if hasattr(context.requirements, "mass_result") and mass_res.winning_candidate:
            geom_result = mass_res.winning_candidate.derived_variables.get("mass_result")
            if geom_result:
                context.requirements.mass_result = geom_result
                context.requirements.mass_properties_result = geom_result


        # 8. Center of Gravity (CG)
        cg_res = self.cg_opt.optimize(context)
        if not cg_res.success:
            raise RuntimeError(f"CGOptimizer failed: {cg_res.message}")
        context.previous_specifications["CGSpecification"] = cg_res.generated_specification
        context.previous_specifications["CGOptimizer"] = cg_res.generated_specification

        # Propagate optimized CG and static margin back to MassPropertiesSpecification and MassResult
        if cg_res.winning_candidate:
            derived = cg_res.winning_candidate.derived_variables
            opt_cg = derived.get("cg_position")
            opt_sm = derived.get("static_margin")
            opt_comps = derived.get("components")

            mass_spec = mass_res.generated_specification
            if mass_spec:
                if opt_cg is not None:
                    mass_spec.center_of_gravity = opt_cg
                if opt_sm is not None:
                    mass_spec.static_margin = opt_sm
                if opt_comps is not None:
                    mass_spec.component_masses = opt_comps

            if hasattr(context.requirements, "mass_result") and context.requirements.mass_result:
                mr = context.requirements.mass_result
                if opt_cg is not None:
                    mr.center_of_gravity = opt_cg
                if opt_sm is not None:
                    mr.static_margin = opt_sm
                if opt_comps is not None:
                    mr.component_masses = opt_comps
                    from backend.design.fixed_wing.mass_properties.inertia_calculator import InertiaCalculator
                    ixx, iyy, izz = InertiaCalculator().calculate_moments_of_inertia(
                        opt_comps, opt_cg[0], opt_cg[1], opt_cg[2]
                    )
                    mr.moments_of_inertia = (round(ixx, 4), round(iyy, 4), round(izz, 4))
                    if mass_spec:
                        mass_spec.moments_of_inertia = mr.moments_of_inertia
                if hasattr(context.requirements, "mass_properties_result"):
                    context.requirements.mass_properties_result = mr

        # 9. Flight Performance
        perf_res = self.perf_opt.optimize(context)
        if not perf_res.success:
            raise RuntimeError(f"FlightPerformanceOptimizer failed: {perf_res.message}")
        context.previous_specifications["FlightPerformanceSpecification"] = perf_res.generated_specification
        context.previous_specifications["FlightPerformanceOptimizer"] = perf_res.generated_specification
        if hasattr(context.requirements, "performance_result") and perf_res.winning_candidate:
            geom_result = perf_res.winning_candidate.derived_variables.get("flight_result")
            if geom_result:
                context.requirements.performance_result = geom_result
                context.requirements.flight_performance_result = geom_result

        return {
            "WingPlanformSpecification": wing_res.generated_specification,
            "FuselageSpecification": fuse_res.generated_specification,
            "PayloadPackagingSpecification": payload_res.generated_specification,
            "TailSpecification": tail_res.generated_specification,
            "PropulsionSpecification": prop_res.generated_specification,
            "ElectricalSystemSpecification": elec_res.generated_specification,
            "MassPropertiesSpecification": mass_res.generated_specification,
            "CGSpecification": cg_res.generated_specification,
            "FlightPerformanceSpecification": perf_res.generated_specification,
        }
