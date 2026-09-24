import math
from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.frame.frame_models import FrameContext, FrameCandidate
from backend.design.multirotor.frame.frame_geometry import FrameGeometry, FrameGeometryGenerator
from backend.design.multirotor.frame.frame_constraints import FrameConstraintsEvaluator
from backend.design.multirotor.frame.frame_selector import FrameSelector, CatalogFrameRecord
from backend.design.multirotor.frame.frame_result import FrameSpecification
from backend.design.multirotor.frame.frame_validator import FrameValidator

class FrameOptimizer(OptimizerBase):
    """
    Multidisciplinary Frame Sizer and Optimizer Subsystem.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "FrameOptimizer") -> None:
        super().__init__(name)
        self._selector = FrameSelector()
        self._validator = FrameValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Generates both Catalog-based and Parametric design candidates.
        """
        assert isinstance(context, FrameContext)
        
        candidates: List[OptimizationCandidate] = []
        strategy = context.strategy_spec
        config = strategy.recommended_configuration_class
        max_frame_size = strategy.constraint_summary.maximum_frame_size_m
        
        # 1. Generate Catalog Selection Candidates
        matching_records = self._selector.get_matching_frames(config, max_frame_size)
        for record in matching_records:
            d_vars = {
                "approach": "Catalog Selection",
                "name": record.name,
                "wheelbase_m": record.wheelbase_m,
                "arm_diameter_m": record.arm_diameter_m,
                "max_propeller_diameter_m": record.max_propeller_diameter_m,
                "landing_gear_height_m": record.landing_gear_height_m,
                "mass_kg": record.empty_mass_kg,
            }
            candidates.append(FrameCandidate(design_variables=d_vars))

        # 2. Generate Parametric Sizing Candidates
        # Generate custom sizes from minimum spacing to maximum allowed size
        min_wheelbase = max(0.20, context.payload_dimensions_m[0] * 2.0)
        max_wheelbase = max_frame_size
        
        # Sizing range increments
        steps = 5
        delta = (max_wheelbase - min_wheelbase) / max(1, steps)
        
        # Size diameters and arms based on payload weight class
        payload = context.payload_weight_kg
        if payload < 0.5:
            arm_d = 0.008
            prop_ratio = 0.45
        elif payload <= 1.5:
            arm_d = 0.012
            prop_ratio = 0.40
        elif payload <= 5.0:
            arm_d = 0.016
            prop_ratio = 0.38
        else:
            arm_d = 0.025
            prop_ratio = 0.35

        for i in range(steps + 1):
            wb = round(min_wheelbase + i * delta, 3)
            if wb > max_frame_size:
                continue
            
            d_vars = {
                "approach": "Parametric Generation",
                "name": f"Custom Carbon {int(wb * 1000)}mm",
                "wheelbase_m": wb,
                "arm_diameter_m": arm_d,
                "max_propeller_diameter_m": round(prop_ratio * wb, 3),
                "landing_gear_height_m": round(context.payload_dimensions_m[2] + 0.08, 3),
                "mass_kg": 0.0,  # Sized dynamically in evaluate
            }
            candidates.append(FrameCandidate(design_variables=d_vars))

        return candidates

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to structural constraint checker rules.
        """
        assert isinstance(candidate, FrameCandidate)
        assert isinstance(context, FrameContext)
        
        # Ensure candidate derived variables and geometry are evaluated before checking constraints
        if candidate.geometry is None:
            self.evaluate_candidate(candidate, context)
            
        passed = FrameConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Calculates coordinates, mass, and clearances for a design candidate.
        """
        assert isinstance(candidate, FrameCandidate)
        assert isinstance(context, FrameContext)
        
        d_vars = candidate.design_variables
        approach = d_vars["approach"]
        wb = d_vars["wheelbase_m"]
        arm_d = d_vars["arm_diameter_m"]
        
        # Configuration properties
        config = context.strategy_spec.recommended_configuration_class
        config_clean = config.lower().replace(" ", "").replace("copter", "")
        
        # Rotor counts
        if "tri" in config_clean:
            arm_count = 3
        elif "quad" in config_clean:
            arm_count = 4
        elif "hex" in config_clean:
            arm_count = 6
        elif "octo" in config_clean:
            arm_count = 8
        elif "coaxial" in config_clean or "x8" in config_clean:
            arm_count = 8
        else:
            arm_count = 4

        # Generate motor positions (x, y, z)
        arm_len = wb / 2.0
        coords = FrameGeometryGenerator.generate_motor_coordinates(config, arm_len)
        
        # Sized payload bay dimensions
        pay_l, pay_w, pay_h = context.payload_dimensions_m
        bay_l = max(pay_l + 0.02, 0.25 * wb)
        bay_w = max(pay_w + 0.02, 0.15 * wb)
        bay_h = d_vars["landing_gear_height_m"]
        
        # Clearance calculations
        landing_gear = d_vars["landing_gear_height_m"]
        clearance = landing_gear
        
        # Size frame envelope
        envelope = (wb + d_vars["max_propeller_diameter_m"], wb + d_vars["max_propeller_diameter_m"], landing_gear + 0.05)
        
        # Mass Sizing
        if approach == "Catalog Selection":
            frame_mass = d_vars["mass_kg"]
        else:
            # Parametric weight calculation: carbon fiber tube density ~ 1600 kg/m³
            # effective physical arms
            eff_arms = 4 if "coaxial" in config_clean or "x8" in config_clean else arm_count
            arm_thickness = 0.002
            d_inner = arm_d - 2.0 * arm_thickness
            arm_volume = eff_arms * arm_len * (math.pi / 4.0) * (arm_d**2 - d_inner**2)
            arm_mass = arm_volume * 1600.0
            
            # Center plates mass scales with payload class
            center_plates = 0.05 + 0.08 * context.payload_weight_kg
            landing_gear_mass = 0.03 * (landing_gear / 0.1)
            frame_mass = round(arm_mass + center_plates + landing_gear_mass, 4)
            
        geom = FrameGeometry(
            configuration=config,
            wheelbase_m=wb,
            arm_length_m=arm_len,
            arm_diameter_m=arm_d,
            arm_count=arm_count,
            motor_positions=coords,
            payload_bay_dimensions_m=(bay_l, bay_w, bay_h),
            landing_gear_height_m=landing_gear,
            ground_clearance_m=clearance,
            envelope_dimensions_m=envelope
        )
        
        candidate.geometry = geom
        candidate.frame_mass_kg = frame_mass
        candidate.derived_variables = {
            "mass_kg": frame_mass,
            "clearance_m": clearance,
            "envelope": envelope,
            "d_hub": 2.0 * arm_len * math.sin(math.radians(360.0 / max(3, arm_count)) / 2.0)
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Scores candidate by combining objective functions and strategy weightings.
        """
        assert isinstance(candidate, FrameCandidate)
        assert isinstance(context, FrameContext)
        
        weights = context.strategy_spec.priority_weights
        geom = candidate.geometry
        
        # 1. Low Mass score (normalize by max possible frame mass)
        mass_score = max(0.0, 1.0 - (candidate.frame_mass_kg / 5.0))
        
        # 2. Rigidity score (arm thickness relative to max 30mm)
        rigidity_score = min(1.0, geom.arm_diameter_m / 0.03)
        
        # 3. Payload fit score
        pay_fit = 1.0 if candidate.payload_fit_passed else 0.0
        
        # 4. Manufacturability
        manufacture_score = 1.0 if candidate.design_variables["approach"] == "Catalog Selection" else 0.8
        
        # 5. Drag score
        drag_score = max(0.0, 1.0 - (geom.wheelbase_m / 2.0))
        
        # Sizing weighted score terms
        weighted_sum = (
            weights.endurance * mass_score +
            weights.efficiency * drag_score +
            weights.payload_capacity * pay_fit +
            weights.reliability * rigidity_score +
            weights.manufacturability * manufacture_score
        )
        
        weights_total = (
            weights.endurance +
            weights.efficiency +
            weights.payload_capacity +
            weights.reliability +
            weights.manufacturability
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "mass_score": mass_score,
            "rigidity_score": rigidity_score,
            "payload_fit": pay_fit,
            "manufacturability": manufacture_score,
            "drag_score": drag_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Assembles winning candidate into a FrameSpecification.
        """
        assert isinstance(candidate, FrameCandidate)
        assert isinstance(context, FrameContext)
        
        geom = candidate.geometry
        reasoning = (
            f"Optimized structure using {candidate.design_variables['approach']} matching "
            f"{geom.configuration} layout. Wheelbase sized to {int(geom.wheelbase_m * 1000)}mm "
            f"with structural strength margin {candidate.structural_margin:.2f}."
        )
        
        spec = FrameSpecification(
            configuration=geom.configuration,
            wheelbase_m=geom.wheelbase_m,
            arm_length_m=geom.arm_length_m,
            arm_diameter_m=geom.arm_diameter_m,
            arm_count=geom.arm_count,
            motor_coordinates=geom.motor_positions,
            payload_bay_dimensions_m=geom.payload_bay_dimensions_m,
            landing_gear_height_m=geom.landing_gear_height_m,
            ground_clearance_m=geom.ground_clearance_m,
            frame_mass_kg=candidate.frame_mass_kg,
            envelope_dimensions_m=geom.envelope_dimensions_m,
            structural_safety_margin=candidate.structural_margin,
            approach_type=candidate.design_variables["approach"],
            selected_name=candidate.design_variables["name"],
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning
        )
        
        # Self validate spec
        self._validator.validate_frame(spec)
        return spec
