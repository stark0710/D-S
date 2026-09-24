"""
Fixed-Wing Fuselage Sizer Subsystem

Purpose:
    Defines the `FuselageSizer` class, which handles fuselage lengths, cross sections,
    compartments, and mounting interfaces.

Role in Architecture:
    `FuselageSizer` computes overall size coordinates (nose, tail cone, length, width, height)
    and compartment boundaries.
"""

from typing import Dict, Any, Tuple
from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements, FuselageType
from backend.design.fixed_wing.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.fixed_wing.fuselage.mounting_interfaces import MountingInterfaces


class FuselageSizer:
    """
    Sizing service responsible for solving fuselage and compartment layout equations.
    """

    def size_fuselage_envelope(
        self,
        requirements: FuselageRequirements,
        fineness_ratio: float,
        clearance_margin: float,
        cross_section: str,
        fuselage_type: FuselageType,
    ) -> FuselageGeometry:
        """
        Sizes outer envelope dimensions and internal compartment volumes.
        """
        wing_geom = requirements.wing_result.wing_geometry
        m_profile = requirements.mission_result.mission_profile

        # 1. Total Length (L_f)
        # Conventional layout length is typically 70-85% of wingspan
        if fuselage_type in (FuselageType.FLYING_WING_CENTER, FuselageType.BLENDED_BODY):
            length = wing_geom.mean_aerodynamic_chord_m * 1.5
        else:
            length = wing_geom.span_m * 0.75

        # 2. Nose and Tail cone sections
        nose_length = length * 0.16
        if fuselage_type in (FuselageType.FLYING_WING_CENTER, FuselageType.BLENDED_BODY):
            tail_cone_length = length * 0.10
        else:
            tail_cone_length = length * 0.32

        # 3. Outer width and height based on fineness ratio and clearance constraints
        # Fineness ratio FR = L_f / equiv_diameter
        equiv_diam = length / fineness_ratio
        
        # Enforce minimum sizes for component clearance (e.g. payload block)
        payload_mass = m_profile.payload_kg
        min_payload_width = 0.08 + (payload_mass * 0.005)  # payload gets wider as mass increases
        min_width = min_payload_width + 2.0 * clearance_margin

        width = max(min_width, equiv_diam * 0.9)
        height = max(min_width * 1.1, equiv_diam * 1.1)

        # 4. Mount attachment locations from nose
        layout = requirements.configuration_result
        is_pusher = layout is not None and "pusher" in getattr(layout, "propulsion_configuration", "Tractor").lower()
        if is_pusher:
            wing_attach_x = length * 0.41
        else:
            wing_attach_x = length * 0.32
        if fuselage_type in (FuselageType.FLYING_WING_CENTER, FuselageType.BLENDED_BODY):
            tail_attach_x = length * 0.90
        else:
            tail_attach_x = length * 0.95

        # 5. Compartment sizing
        # Payload bay
        pay_len = length * 0.22
        pay_wid = width - 2.0 * clearance_margin
        pay_hgt = height * 0.75
        pay_vol = pay_len * pay_wid * pay_hgt

        # Battery bay
        bat_len = length * 0.16
        bat_wid = width - 2.0 * clearance_margin
        bat_hgt = height * 0.55
        bat_vol = bat_len * bat_wid * bat_hgt

        # Avionics bay
        av_len = length * 0.14
        av_wid = width - 2.0 * clearance_margin
        av_hgt = height * 0.35

        # Total Volume approximation (Fuselage is approximated as a cylinder/prism tapering at nose and tail cone)
        total_vol = width * height * (length - 0.5 * (nose_length + tail_cone_length))

        return FuselageGeometry(
            length_m=round(length, 3),
            width_m=round(width, 3),
            height_m=round(height, 3),
            nose_length_m=round(nose_length, 3),
            tail_cone_length_m=round(tail_cone_length, 3),
            cross_section_type=cross_section,
            wing_attachment_x_m=round(wing_attach_x, 3),
            tail_attachment_x_m=round(tail_attach_x, 3),
            
            payload_bay_length_m=round(pay_len, 3),
            payload_bay_width_m=round(pay_wid, 3),
            payload_bay_height_m=round(pay_hgt, 3),
            payload_bay_volume_m3=round(pay_vol, 6),
            
            battery_bay_length_m=round(bat_len, 3),
            battery_bay_width_m=round(bat_wid, 3),
            battery_bay_height_m=round(bat_hgt, 3),
            battery_bay_volume_m3=round(bat_vol, 6),
            
            avionics_bay_length_m=round(av_len, 3),
            avionics_bay_width_m=round(av_wid, 3),
            avionics_bay_height_m=round(av_hgt, 3),
            
            total_volume_m3=round(total_vol, 5),
        )

    def size_mounting_interfaces(
        self,
        geometry: FuselageGeometry,
        requirements: FuselageRequirements,
        fuselage_type: FuselageType,
    ) -> MountingInterfaces:
        """
        Sizes landing gear positions and attachment bolts hardware.
        """
        layout = requirements.configuration_result.selected_configuration
        prop_layout = layout.get("propulsion_layout", "Tractor")
        gear_layout = layout.get("landing_gear_configuration", "Tricycle")

        # Wing connection
        wing_hardware = "4x M4 steel bolts with blind nuts"
        wing_style = "Saddle Mount with rubber dampers"

        # Tail attachment
        if fuselage_type == FuselageType.POD_AND_BOOM:
            tail_style = "Carbon fiber boom tube clamp (20mm diam)"
        elif fuselage_type == FuselageType.TWIN_BOOM:
            tail_style = "Dual CF boom sleeve mounts integrated in wing root bulkheads"
        else:
            tail_style = "Integrated rear fuselage bulkheads"

        # Firewall
        if "Tractor" in prop_layout:
            prop_mount = "Front bulkhead firewall: 55x55mm 3.0mm carbon fiber panel"
        elif "Pusher" in prop_layout:
            prop_mount = "Rear tail cone firewall: 45x45mm 3.0mm carbon fiber panel"
        else:
            prop_mount = "Twin wing-pod firewalls"

        # Landing Gear attachment points
        # Main gear is located slightly aft of CG
        wing_x = geometry.wing_attachment_x_m
        if gear_layout == "Tricycle":
            main_gear_x = wing_x + 0.08
            nose_gear_x = geometry.nose_length_m * 0.5
            gear_style = "Tricycle retract mount plates"
        elif gear_layout == "Taildragger":
            main_gear_x = wing_x - 0.04  # forward of CG
            nose_gear_x = geometry.length_m - 0.05  # tail wheel
            gear_style = "Taildragger carbon spring landing gear bracket"
        else:
            main_gear_x = 0.0
            nose_gear_x = 0.0
            gear_style = "Belly Landing skid plate mounting block"

        return MountingInterfaces(
            wing_mounting_style=wing_style,
            wing_mounting_hardware=wing_hardware,
            tail_mounting_style=tail_style,
            propulsion_mount_type=prop_mount,
            landing_gear_mount_type=gear_style,
            main_gear_attachment_x_m=round(main_gear_x, 3),
            nose_gear_attachment_x_m=round(nose_gear_x, 3),
            access_panels_description="1x Top main electronics hatch with spring latch, 1x bottom payload bay access hatch",
        )
