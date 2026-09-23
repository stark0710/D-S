import math
from typing import List, Any
from backend.design.common.optimization.optimizer_base import OptimizerBase
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.multirotor.layout.layout_models import LayoutContext, LayoutCandidate
from backend.design.multirotor.layout.component_packager import ComponentPackager, BoundingBox3D
from backend.design.multirotor.layout.mounting_selector import MountingSelector
from backend.design.multirotor.layout.layout_constraints import LayoutConstraintsEvaluator
from backend.design.multirotor.layout.layout_validator import LayoutValidator
from backend.design.multirotor.layout.layout_result import LayoutSpecification

class LayoutEngine(OptimizerBase):
    """
    Multidisciplinary Component Packaging, Collision Detection, and Mount Selection Engine.
    Adapts the shared OptimizerBase template method lifecycle.
    """
    def __init__(self, name: str = "LayoutEngine") -> None:
        super().__init__(name)
        self._validator = LayoutValidator()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """
        Generates alternative internal component layouts.
        """
        assert isinstance(context, LayoutContext)
        
        req = context.requirements
        battery_weight = context.propulsion_assembly.battery.weight_kg
        payload_dims = req.metadata.get("payload_dimensions_m", (0.15, 0.10, 0.08))
        
        # Calculate dynamic heights of battery and payload to implement vertical stacking
        vol = battery_weight / 2000.0
        side = vol ** (1.0 / 3.0)
        batt_dz = side * 0.8
        payload_dz = payload_dims[2]
        
        candidates: List[OptimizationCandidate] = []
        
        # Topology 1: Battery Top / Payload Bottom Center (Standard configuration)
        # Keeps battery easily swappable and payload suspended centrally
        cand1 = LayoutCandidate(design_variables={"topology": "BatteryTop_PayloadBottom"})
        cand1.boxes = {
            "FlightController": ComponentPackager.get_fc_envelope(0.0, 0.0, 0.01),
            "PowerDistributionBoard": ComponentPackager.get_pdb_envelope(0.0, 0.0, -0.015),
            "GPSReceiver": ComponentPackager.get_gps_envelope(0.0, 0.0, 0.15),
            "TelemetryModem": ComponentPackager.get_telemetry_envelope(0.06, 0.0, -0.015),
            "RcReceiver": ComponentPackager.get_receiver_envelope(-0.05, 0.0, 0.01),
            "BatteryPack": ComponentPackager.get_battery_envelope(0.0, 0.0, 0.03 + 0.5 * batt_dz, battery_weight),
            "PayloadBay": ComponentPackager.get_payload_envelope(0.0, 0.0, -0.0325 - 0.5 * payload_dz, payload_dims)
        }
        candidates.append(cand1)

        # Topology 2: Battery Bottom Rear / Payload Bottom Front (Balanced configuration)
        # Offsets battery weight against payload weight across horizontal arms
        cand2 = LayoutCandidate(design_variables={"topology": "BatteryBottomRear_PayloadBottomFront"})
        cand2.boxes = {
            "FlightController": ComponentPackager.get_fc_envelope(0.0, 0.0, 0.01),
            "PowerDistributionBoard": ComponentPackager.get_pdb_envelope(0.0, 0.0, -0.015),
            "GPSReceiver": ComponentPackager.get_gps_envelope(0.0, 0.0, 0.15),
            "TelemetryModem": ComponentPackager.get_telemetry_envelope(0.0, 0.06, -0.015),
            "RcReceiver": ComponentPackager.get_receiver_envelope(0.0, -0.05, 0.01),
            "BatteryPack": ComponentPackager.get_battery_envelope(-0.08, 0.0, -0.0325 - 0.5 * batt_dz, battery_weight),
            "PayloadBay": ComponentPackager.get_payload_envelope(0.08, 0.0, -0.0325 - 0.5 * payload_dz, payload_dims)
        }
        candidates.append(cand2)

        # Topology 3: Sandwich Compact (FC and Battery on same plane)
        # Highly compact but has a collision overlap (will be rejected by spatial checker)
        cand3 = LayoutCandidate(design_variables={"topology": "SandwichCompact_Collision"})
        cand3.boxes = {
            "FlightController": ComponentPackager.get_fc_envelope(0.0, 0.0, 0.01),
            "PowerDistributionBoard": ComponentPackager.get_pdb_envelope(0.0, 0.0, -0.015),
            "GPSReceiver": ComponentPackager.get_gps_envelope(0.0, 0.0, 0.05),  # GPS too low
            "TelemetryModem": ComponentPackager.get_telemetry_envelope(0.0, 0.0, 0.01),
            "RcReceiver": ComponentPackager.get_receiver_envelope(0.0, 0.0, 0.01),
            "BatteryPack": ComponentPackager.get_battery_envelope(0.0, 0.0, 0.01, battery_weight),  # Direct overlap with FC
            "PayloadBay": ComponentPackager.get_payload_envelope(0.0, 0.0, -0.06, payload_dims)
        }
        candidates.append(cand3)

        # Assign mounting profiles to all candidates
        for cand in candidates:
            cand.mounts = {
                name: MountingSelector.get_mount_for_component(name)
                for name in cand.boxes.keys()
            }
            
        return candidates

    def apply_constraints(self, candidate: OptimizationCandidate, context: OptimizationContext) -> bool:
        """
        Redirects to constraints checkers.
        """
        assert isinstance(candidate, LayoutCandidate)
        assert isinstance(context, LayoutContext)
        
        if len(candidate.constraint_results) == 0:
            self.evaluate_candidate(candidate, context)
            
        passed = LayoutConstraintsEvaluator.evaluate_constraints(candidate, context)
        return passed

    def evaluate_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Calculates clearances, packaging efficiency, CG offsets, and accessibility.
        """
        assert isinstance(candidate, LayoutCandidate)
        assert isinstance(context, LayoutContext)
        
        fc = candidate.boxes.get("FlightController")
        batt = candidate.boxes.get("BatteryPack")
        gps = candidate.boxes.get("GPSReceiver")
        pdb = candidate.boxes.get("PowerDistributionBoard")
        payload = candidate.boxes.get("PayloadBay")
        
        # 1. FC to Battery clearance
        if fc and batt:
            dx = fc.x_c - batt.x_c
            dy = fc.y_c - batt.y_c
            dz = fc.z_c - batt.z_c
            candidate.fc_to_battery_clearance_m = max(0.0, math.sqrt(dx**2 + dy**2 + dz**2) - 0.5 * (fc.dz + batt.dz))
            
        # 2. GPS to PDB clearance
        if gps and pdb:
            dx = gps.x_c - pdb.x_c
            dy = gps.y_c - pdb.y_c
            dz = gps.z_c - pdb.z_c
            candidate.gps_to_pdb_clearance_m = math.sqrt(dx**2 + dy**2 + dz**2)

        # 3. CG Offset estimation (mass center shift from geometry center)
        m_batt = context.propulsion_assembly.battery.weight_kg
        m_payload = context.requirements.payload_weight_kg
        
        x_batt = batt.x_c if batt else 0.0
        x_payload = payload.x_c if payload else 0.0
        
        # CG offset along x axis: (M1*X1 + M2*X2) / Total Mass
        # Approximate aircraft empty weight excluding battery & payload = 1.8 kg
        m_empty = 1.8
        candidate.cg_offset_from_center_m = abs((m_batt * x_batt + m_payload * x_payload) / (m_batt + m_payload + m_empty))

        # 4. Packaging Efficiency (ratio of component volumes to frame available volume)
        # Estimate frame available inner deck volume (wheelbase ^ 3 / 25)
        w = context.frame_spec.wheelbase_m
        vol_frame = (w ** 3) / 25.0
        
        vol_components = sum(box.dx * box.dy * box.dz for box in candidate.boxes.values())
        candidate.packaging_efficiency_pct = min(100.0, (vol_components / max(0.001, vol_frame)) * 100.0)

        # 5. Accessibility Score
        topo = candidate.design_variables.get("topology")
        if topo == "BatteryTop_PayloadBottom":
            candidate.accessibility_score = 95.0  # Top mounted battery is easiest to swap
        elif topo == "BatteryBottomRear_PayloadBottomFront":
            candidate.accessibility_score = 80.0
        else:
            candidate.accessibility_score = 30.0  # Sandwiched/internal is very hard to swap
            
        # Save derived variables in dictionary for logger compatibility
        candidate.derived_variables = {
            "accessibility_score": candidate.accessibility_score,
            "packaging_efficiency_pct": candidate.packaging_efficiency_pct,
            "cg_offset_from_center_m": candidate.cg_offset_from_center_m
        }

    def score_candidate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> float:
        """
        Calculates optimization score using mission priorities.
        """
        assert isinstance(candidate, LayoutCandidate)
        assert isinstance(context, LayoutContext)
        
        weights = context.strategy_spec.priority_weights
        
        # 1. CG Proximity score (favor zero offset, normalized relative to 0.15m limit)
        cg_score = max(0.0, 1.0 - (candidate.cg_offset_from_center_m / 0.15))
        
        # 2. Accessibility score
        access_score = candidate.accessibility_score / 100.0
        
        # 3. Packaging density score
        density_score = candidate.packaging_efficiency_pct / 100.0
        
        weighted_sum = (
            weights.safety * cg_score +
            weights.endurance * access_score +
            weights.reliability * density_score
        )
        
        weights_total = (
            weights.safety +
            weights.endurance +
            weights.reliability
        )
        
        score = weighted_sum / max(0.01, weights_total)
        candidate.overall_score = score
        candidate.objective_scores = {
            "cg_proximity": cg_score,
            "accessibility": access_score,
            "packaging_density": density_score
        }
        return score

    def build_specification(self, candidate: OptimizationCandidate, context: OptimizationContext) -> Any:
        """
        Converts optimized candidate to LayoutSpecification.
        """
        assert isinstance(candidate, LayoutCandidate)
        assert isinstance(context, LayoutContext)
        
        coords = {
            name: (box.x_c, box.y_c, box.z_c)
            for name, box in candidate.boxes.items()
        }
        
        cable_routing = {
            "Power Cables": "Routed along the bottom plate deck from PDB to ESC inputs using protective high-temp sleeves.",
            "Signal Cables": "Routed along internal structural posts with ferrite rings to block electromagnetic induction noise."
        }
        
        cooling_zones = [
            "Upper Plate Exhaust Zone (forced convection from motor wash)",
            "ESC arm cooling zones (exposed to active propeller slipstream)"
        ]
        
        maint_zones = [
            "Top Plate Battery swap deck (quick access)",
            "Bottom plate rail clamp (payload separation bracket)"
        ]
        
        reasoning = (
            f"Generated spatial coordinates packaging {len(coords)} components. selected topology "
            f"'{candidate.design_variables.get('topology')}' achieving accessibility rating {candidate.accessibility_score:.1f}% "
            f"and packing efficiency {candidate.packaging_efficiency_pct:.1f}% while ensuring "
            f"mass offset is minimized to {candidate.cg_offset_from_center_m * 1000.0:.1f} mm."
        )
        
        spec = LayoutSpecification(
            component_coordinates=coords,
            mounting_locations=candidate.mounts,
            cable_routing=cable_routing,
            payload_mount=candidate.mounts.get("PayloadBay", "Standard Rail Clamp"),
            cooling_zones=cooling_zones,
            maintenance_zones=maint_zones,
            accessibility_score=candidate.accessibility_score,
            packaging_efficiency_pct=candidate.packaging_efficiency_pct,
            optimization_score=candidate.overall_score,
            engineering_reasoning=reasoning
        )
        
        # Validate spec
        self._validator.validate_layout(spec)
        return spec
