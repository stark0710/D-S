import math
from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.mass_properties.mass_models import MassPropertiesContext, MassPropertiesCandidate
from backend.design.multirotor.mass_properties.cg_calculator import CgCalculator
from backend.design.multirotor.mass_properties.inertia_calculator import InertiaCalculator
from backend.design.multirotor.mass_properties.weight_breakdown import WeightBreakdown, WeightBreakdownResult
from backend.design.multirotor.mass_properties.mass_constraints import MassConstraintsEvaluator
from backend.design.multirotor.mass_properties.mass_validator import MassValidator
from backend.design.multirotor.mass_properties.mass_result import MassPropertiesSpecification

class MassPropertiesEngine(OptimizerBase):
    """
    Multidisciplinary Center of Gravity & Inertia Tensor Optimization Engine.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "MassPropertiesEngine") -> None:
        super().__init__(name)
        self._validator = MassValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Captures the layout assembly to evaluate its rigid mass properties.
        """
        assert isinstance(context, MassPropertiesContext)
        
        # Sizing empty mass & structure is unique to the selected layout
        cand = MassPropertiesCandidate(design_variables={"layout_type": "LayoutDesignSpecification"})
        return [cand]

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to constraints checkers.
        """
        assert isinstance(candidate, MassPropertiesCandidate)
        assert isinstance(context, MassPropertiesContext)
        
        if candidate.weight_breakdown is None:
            self.evaluate_candidate(candidate, context)
            
        passed = MassConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Computes Center of Gravity coordinates, inertia tensors, and category breakdown.
        """
        assert isinstance(candidate, MassPropertiesCandidate)
        assert isinstance(context, MassPropertiesContext)
        
        frame = context.frame_spec
        motor = context.propulsion_assembly.motor
        prop = context.propulsion_assembly.propeller
        esc = context.propulsion_assembly.esc
        batt = context.propulsion_assembly.battery
        coords = context.layout_spec.component_coordinates
        
        # Estimate main wire mass from wiring sizer outputs (default AWG 14 = 24g/m)
        wire_weight = 0.05
        pdb_weight = 0.025
        
        # 1. CG Balancing: Optimize battery position coordinates for lateral balance
        balanced_coords = CgCalculator.balance_battery(
            coords=coords,
            m_payload=context.requirements.payload_weight_kg,
            m_battery=batt.weight_kg,
            m_frame=frame.frame_mass_kg,
            m_motor=motor.weight_kg,
            m_prop=prop.weight_kg,
            m_esc=esc.weight_kg,
            m_wire=wire_weight,
            m_pdb=pdb_weight,
            arm_count=frame.arm_count,
            wheelbase_m=frame.wheelbase_m,
            motor_coords=frame.motor_coordinates
        )
        
        # 2. Evaluate Mass Category Breakdown
        breakdown = WeightBreakdown.calculate_breakdown(
            payload_kg=context.requirements.payload_weight_kg,
            frame_mass_kg=frame.frame_mass_kg,
            motor_weight_kg=motor.weight_kg,
            prop_weight_kg=prop.weight_kg,
            esc_weight_kg=esc.weight_kg,
            battery_weight_kg=batt.weight_kg,
            wire_weight_kg=wire_weight,
            pdb_weight_kg=pdb_weight,
            arm_count=frame.arm_count
        )
        candidate.weight_breakdown = breakdown

        # 3. Evaluate Center of Gravity with balanced coordinates
        cg_x, cg_y, cg_z = CgCalculator.calculate_cg(
            coords=balanced_coords,
            m_payload=context.requirements.payload_weight_kg,
            m_battery=batt.weight_kg,
            m_frame=frame.frame_mass_kg,
            m_motor=motor.weight_kg,
            m_prop=prop.weight_kg,
            m_esc=esc.weight_kg,
            m_wire=wire_weight,
            m_pdb=pdb_weight,
            arm_count=frame.arm_count,
            wheelbase_m=frame.wheelbase_m,
            motor_coords=frame.motor_coordinates
        )
        candidate.cg_x_m = cg_x
        candidate.cg_y_m = cg_y
        candidate.cg_z_m = cg_z
        candidate.cg_offset_magnitude_m = math.sqrt(cg_x**2 + cg_y**2)

        # 4. Evaluate Moments of Inertia
        ixx, iyy, izz = InertiaCalculator.calculate_inertia(
            coords=balanced_coords,
            m_payload=context.requirements.payload_weight_kg,
            m_battery=batt.weight_kg,
            m_frame=frame.frame_mass_kg,
            m_motor=motor.weight_kg,
            m_prop=prop.weight_kg,
            m_esc=esc.weight_kg,
            m_wire=wire_weight,
            m_pdb=pdb_weight,
            arm_count=frame.arm_count,
            wheelbase_m=frame.wheelbase_m,
            cg=(cg_x, cg_y, cg_z),
            motor_coords=frame.motor_coordinates
        )
        candidate.ixx_kg_m2 = ixx
        candidate.iyy_kg_m2 = iyy
        candidate.izz_kg_m2 = izz

        # 5. Evaluate Principal Axes of Inertia
        principal_axes = InertiaCalculator.calculate_principal_axes(
            coords=balanced_coords,
            m_payload=context.requirements.payload_weight_kg,
            m_battery=batt.weight_kg,
            m_frame=frame.frame_mass_kg,
            m_motor=motor.weight_kg,
            m_prop=prop.weight_kg,
            m_esc=esc.weight_kg,
            m_wire=wire_weight,
            m_pdb=pdb_weight,
            arm_count=frame.arm_count,
            wheelbase_m=frame.wheelbase_m,
            cg=(cg_x, cg_y, cg_z),
            motor_coords=frame.motor_coordinates
        )
        candidate.principal_axes = principal_axes
        candidate.balanced_coords = balanced_coords

        # Save derived variables in dictionary for logger compatibility
        candidate.derived_variables = {
            "cg_x_m": cg_x,
            "cg_y_m": cg_y,
            "cg_z_m": cg_z,
            "cg_offset_magnitude_m": candidate.cg_offset_magnitude_m,
            "total_mass_kg": breakdown.total_mass_kg,
            "ixx_kg_m2": ixx,
            "iyy_kg_m2": iyy,
            "izz_kg_m2": izz,
            "principal_axes": principal_axes
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates optimization score using mission priorities.
        """
        assert isinstance(candidate, MassPropertiesCandidate)
        assert isinstance(context, MassPropertiesContext)
        
        weights = context.strategy_spec.priority_weights
        breakdown = candidate.weight_breakdown
        
        # 1. CG Proximity score (favor zero lateral offset, normalized to 5cm limit)
        cg_score = max(0.0, 1.0 - (candidate.cg_offset_magnitude_m / 0.05))
        
        # 2. Payload Fraction score (relative to 40% target)
        payload_score = min(1.0, breakdown.payload_fraction / 0.40)
        
        # 3. Structural efficiency (minimizes structural fraction relative to 40% limit)
        structural_score = max(0.0, 1.0 - (breakdown.structural_fraction / 0.40))
        
        weighted_sum = (
            weights.safety * cg_score +
            weights.efficiency * payload_score +
            weights.reliability * structural_score
        )
        
        weights_total = (
            weights.safety +
            weights.efficiency +
            weights.reliability
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "cg_proximity": cg_score,
            "payload_fraction_score": payload_score,
            "structural_efficiency": structural_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Converts optimized candidate to MassPropertiesSpecification.
        """
        assert isinstance(candidate, MassPropertiesCandidate)
        assert isinstance(context, MassPropertiesContext)
        
        breakdown = candidate.weight_breakdown
        
        weight_dict = {
            "Total Takeoff Mass (kg)": breakdown.total_mass_kg,
            "Empty Structural Mass (kg)": breakdown.empty_mass_kg,
            "Payload Weight (kg)": breakdown.payload_mass_kg,
            "Battery Weight (kg)": breakdown.battery_mass_kg,
            "Propulsion Weight (kg)": breakdown.propulsion_mass_kg,
            "Electrical Wire/PDB Weight (kg)": breakdown.electrical_mass_kg,
            "Frame Structure Weight (kg)": breakdown.frame_mass_kg,
            "Avionics Weight (kg)": breakdown.avionics_mass_kg
        }
        
        fraction_dict = {
            "Payload Mass Fraction (%)": breakdown.payload_fraction * 100.0,
            "Battery Mass Fraction (%)": breakdown.battery_fraction * 100.0,
            "Structural Mass Fraction (%)": breakdown.structural_fraction * 100.0
        }
        
        inertia_dict = {
            "Ixx (kg*m^2)": candidate.ixx_kg_m2,
            "Iyy (kg*m^2)": candidate.iyy_kg_m2,
            "Izz (kg*m^2)": candidate.izz_kg_m2
        }
        
        # Balance Checks
        motor_coords = context.frame_spec.motor_coordinates
        if motor_coords and len(motor_coords) > 0:
            sum_mx = sum(c[0] for c in motor_coords)
            sum_my = sum(c[1] for c in motor_coords)
            propulsion_layout_symmetric = (abs(sum_mx) < 1e-4) and (abs(sum_my) < 1e-4)
        else:
            propulsion_layout_symmetric = True
            
        coords = candidate.balanced_coords
        payload_balanced = (abs(coords.get("PayloadBay", (0, 0, 0))[0]) <= 0.01) and (abs(coords.get("PayloadBay", (0, 0, 0))[1]) <= 0.01)
        battery_balanced = (abs(coords.get("BatteryPack", (0, 0, 0))[0]) <= 0.01) and (abs(coords.get("BatteryPack", (0, 0, 0))[1]) <= 0.01)
        electrical_balanced = (abs(coords.get("PowerDistributionBoard", (0, 0, 0))[0]) <= 0.01) and (abs(coords.get("PowerDistributionBoard", (0, 0, 0))[1]) <= 0.01)
        no_excessive_cg_offset = (candidate.cg_offset_magnitude_m <= 0.02)
        
        symmetry_report = {
            "lateral_symmetry_x": abs(candidate.cg_x_m) <= 0.01,
            "lateral_symmetry_y": abs(candidate.cg_y_m) <= 0.01,
            "propulsion_layout_symmetric": propulsion_layout_symmetric,
            "payload_balanced": payload_balanced,
            "battery_balanced": battery_balanced,
            "electrical_balanced": electrical_balanced,
            "no_excessive_cg_offset": no_excessive_cg_offset
        }
        
        reasoning = (
            f"Sized complete mass properties resulting in total takeoff weight of {breakdown.total_mass_kg:.2f} kg "
            f"and empty structural weight of {breakdown.empty_mass_kg:.2f} kg. Center of Gravity coordinates are "
            f"X_cg = {candidate.cg_x_m*1000.0:.1f} mm, Y_cg = {candidate.cg_y_m*1000.0:.1f} mm, "
            f"Z_cg = {candidate.cg_z_m*1000.0:.1f} mm with principal inertia moments "
            f"Ixx = {candidate.ixx_kg_m2:.3f}, Iyy = {candidate.iyy_kg_m2:.3f}, Izz = {candidate.izz_kg_m2:.3f} kg*m^2."
        )
        
        spec = MassPropertiesSpecification(
            total_mass_kg=breakdown.total_mass_kg,
            empty_mass_kg=breakdown.empty_mass_kg,
            payload_mass_kg=breakdown.payload_mass_kg,
            battery_mass_kg=breakdown.battery_mass_kg,
            weight_breakdown=weight_dict,
            component_fractions=fraction_dict,
            center_of_gravity=(candidate.cg_x_m, candidate.cg_y_m, candidate.cg_z_m),
            moments_of_inertia=inertia_dict,
            symmetry_report=symmetry_report,
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning,
            principal_axes=getattr(candidate, "principal_axes", {})
        )
        
        # Validate spec
        self._validator.validate_mass_properties(spec)
        return spec
