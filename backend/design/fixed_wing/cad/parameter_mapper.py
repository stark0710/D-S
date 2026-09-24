"""
Fixed-Wing CAD Parameter Mapper Subsystem

Purpose:
    Defines the `ParameterMapper` class, converting sizing results to CAD parameter dictionaries.

Role in Architecture:
    `ParameterMapper` maps wing chord spans, fuselage dimensions, and tail arm coordinates.
"""

from typing import Dict, Any
from backend.design.fixed_wing.cad.cad_requirements import CADRequirements


class ParameterMapper:
    """
    Mapping service translating aerodynamic sizing variables to CAD parameters.
    """

    def map_parameters(self, requirements: CADRequirements) -> Dict[str, Any]:
        """
        Maps engineering outputs to direct CAD inputs.

        Returns:
            Dict[str, Any]: Parametric CAD dimensions map.
        """
        wing = requirements.wing_result.wing_geometry
        fuse = requirements.fuselage_result.fuselage_geometry
        tail = requirements.tail_result

        params = {
            "wing_span_mm": wing.span_m * 1000.0,
            "wing_root_chord_mm": wing.root_chord_m * 1000.0,
            "wing_tip_chord_mm": wing.tip_chord_m * 1000.0,
            "wing_sweep_deg": wing.sweep_angle_deg,
            "wing_dihedral_deg": wing.dihedral_angle_deg,
            
            "fuselage_length_mm": fuse.length_m * 1000.0,
            "fuselage_width_mm": fuse.width_m * 1000.0,
            "fuselage_height_mm": fuse.height_m * 1000.0,
            
            "tail_configuration": tail.tail_configuration,
            "horizontal_tail_span_mm": tail.horizontal_tail.span_m * 1000.0,
            "vertical_tail_span_mm": tail.vertical_tail.height_m * 1000.0,
        }

        return params
