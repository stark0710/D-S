"""
Fixed-Wing Fuselage Sizing Candidate Evaluator

Evaluates candidate parameters using FuselageEngine with customized sizer and placement overrides.
"""

from typing import Dict, Any
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.common.optimization.candidate_evaluator_base import CandidateEvaluatorBase
from backend.design.fixed_wing.fuselage.fuselage_engine import FuselageEngine
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.fuselage_sizer import FuselageSizer
from backend.design.fixed_wing.fuselage.component_placement import ComponentPlacementService, ComponentPlacement

class OptimizedFuselageSizer(FuselageSizer):
    """
    Overridden FuselageSizer directly returning custom sizing geometries.
    """
    def __init__(self, override_geometry: FuselageGeometry) -> None:
        super().__init__()
        self._override = override_geometry

    def size_fuselage_envelope(self, *args, **kwargs) -> FuselageGeometry:
        return self._override

class OptimizedComponentPlacementService(ComponentPlacementService):
    """
    Overridden ComponentPlacementService directly returning custom placement coordinates.
    """
    def __init__(self, override_placement: ComponentPlacement) -> None:
        super().__init__()
        self._override = override_placement

    def place_components(self, *args, **kwargs) -> ComponentPlacement:
        return self._override

class CandidateEvaluator(CandidateEvaluatorBase):
    """
    Fuselage candidate evaluator running standard FuselageEngine sizing tools.
    """
    def __init__(self, engine: FuselageEngine | None = None) -> None:
        self._engine = engine if engine else FuselageEngine()

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        reqs = context.requirements
        vars_ = candidate.design_variables
        
        l = vars_["length"]
        w = vars_["width"]
        h = vars_["height"]
        nose_l = vars_["nose_length"]
        tail_cone_l = vars_["tail_cone_length"]
        cs = vars_["cross_section"]
        
        clearance = 0.015
        
        # 1. Outer dimensions and compartments sizing
        pay_len = round(l * 0.22, 3)
        pay_wid = round(w - 2.0 * clearance, 3)
        pay_hgt = round(h * 0.75, 3)
        pay_vol = round(pay_len * pay_wid * pay_hgt, 5)

        bat_len = round(l * 0.16, 3)
        bat_wid = round(w - 2.0 * clearance, 3)
        bat_hgt = round(h * 0.55, 3)
        bat_vol = round(bat_len * bat_wid * bat_hgt, 5)

        av_len = round(l * 0.14, 3)
        av_wid = round(w - 2.0 * clearance, 3)
        av_hgt = round(h * 0.35, 3)

        total_vol = round(w * h * (l - 0.5 * (nose_l + tail_cone_l)), 5)
        
        layout = reqs.configuration_result
        is_pusher = layout is not None and "pusher" in getattr(layout, "propulsion_configuration", "Tractor").lower()
        if is_pusher:
            wing_attach_x = round(l * 0.41, 3)
        else:
            wing_attach_x = round(l * 0.32, 3)
        tail_attach_x = round(l * 0.95, 3)

        override_geometry = FuselageGeometry(
            length_m=l,
            width_m=w,
            height_m=h,
            nose_length_m=nose_l,
            tail_cone_length_m=tail_cone_l,
            cross_section_type=cs,
            wing_attachment_x_m=wing_attach_x,
            tail_attachment_x_m=tail_attach_x,
            payload_bay_length_m=pay_len,
            payload_bay_width_m=pay_wid,
            payload_bay_height_m=pay_hgt,
            payload_bay_volume_m3=pay_vol,
            battery_bay_length_m=bat_len,
            battery_bay_width_m=bat_wid,
            battery_bay_height_m=bat_hgt,
            battery_bay_volume_m3=bat_vol,
            avionics_bay_length_m=av_len,
            avionics_bay_width_m=av_wid,
            avionics_bay_height_m=av_hgt,
            total_volume_m3=total_vol
        )

        # 2. Components balance placement
        payload_x = round(wing_attach_x + 0.1, 3)
        battery_x = round(wing_attach_x - 0.05, 3)
        fc_x = round(wing_attach_x + 0.2, 3)
        gps_x = round(wing_attach_x + 0.22, 3)
        receiver_x = round(wing_attach_x + 0.24, 3)
        telemetry_x = round(wing_attach_x + 0.26, 3)
        esc_x = round(wing_attach_x - 0.1, 3)
        motor_x = round(l * 0.05, 3)

        payload_mass = reqs.mission_result.mission_profile.payload_kg if reqs.mission_result else 2.0

        override_placement = ComponentPlacement(
            calculated_cg_x_m=round(wing_attach_x + 0.05, 3),
            target_cg_x_m=round(wing_attach_x + 0.05, 3),
            static_margin_pct=15.0,
            component_locations={
                "Payload": payload_x,
                "Battery": battery_x,
                "FlightController": fc_x,
                "GPS": gps_x,
                "Receiver": receiver_x,
                "Telemetry": telemetry_x,
                "ESC": esc_x,
                "Motor": motor_x
            },
            component_masses={
                "Structure": 1.5,
                "Payload": payload_mass,
                "Battery": 1.2,
                "Motor": 0.4
            }
        )

        orig_sizer = self._engine._sizer
        orig_placement_service = self._engine._placement_service
        
        self._engine._sizer = OptimizedFuselageSizer(override_geometry)
        self._engine._placement_service = OptimizedComponentPlacementService(override_placement)

        try:
            res = self._engine.process_fuselage_design(reqs)
            candidate.derived_variables["fuselage_result"] = res
            candidate.derived_variables["overall_length"] = l
            candidate.derived_variables["width"] = w
            candidate.derived_variables["height"] = h
            candidate.derived_variables["payload_bay"] = {
                "length": pay_len,
                "width": pay_wid,
                "height": pay_hgt,
                "position_x": payload_x,
                "volume": pay_vol
            }
            candidate.derived_variables["battery_bay"] = {
                "length": bat_len,
                "width": bat_wid,
                "height": bat_hgt,
                "position_x": battery_x,
                "volume": bat_vol
            }
            candidate.derived_variables["avionics_bay"] = {
                "length": av_len,
                "width": av_wid,
                "height": av_hgt,
                "position_x": fc_x
            }
        finally:
            self._engine._sizer = orig_sizer
            self._engine._placement_service = orig_placement_service
