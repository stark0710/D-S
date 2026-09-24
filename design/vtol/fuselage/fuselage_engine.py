"""
VTOL Fuselage Sizing Engine Subsystem

Purpose:
    Defines the `FuselageEngine` facade class orchestrating external geometry,
    compartment packaging partitions, internal subsystem CG balancing,
    hardpoint mounting interfaces, and thermal cooling pathways.
"""

from typing import List, Dict, Any
import math
from datetime import datetime

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.vtol.fuselage.fuselage_result import FuselageResult
from backend.design.vtol.fuselage.fuselage_geometry import FuselageGeometry
from backend.design.vtol.fuselage.fuselage_structure import FuselageStructure
from backend.design.vtol.fuselage.internal_layout import SubsystemPlacement, InternalLayout
from backend.design.vtol.fuselage.compartment_layout import Compartment, CompartmentLayout
from backend.design.vtol.fuselage.mounting_interfaces import MountingInterface, MountingInterfaces
from backend.design.vtol.fuselage.cooling_layout import CoolingInlet, CoolingLayout
from backend.design.vtol.fuselage.landing_gear_interfaces import GearAttachmentPoint, LandingGearInterfaces
from backend.design.vtol.fuselage.boom_interfaces import BoomAttachmentPoint, BoomInterfaces
from backend.design.vtol.fuselage.fuselage_analysis import FuselageAnalysis
from backend.design.vtol.fuselage.fuselage_validator import FuselageValidator
from backend.design.vtol.fuselage.fuselage_registry import VTOLFuselageStrategyRegistry
from backend.design.vtol.fuselage.fuselage_profile import FuselageProfile


class FuselageEngine:
    """
    Facade orchestrator driving fuselage packaging, interfaces, and CG static audits.
    """

    def __init__(
        self,
        validator: FuselageValidator | None = None,
        profile: FuselageProfile | None = None,
    ) -> None:
        self._validator = validator or FuselageValidator()
        self._profile = profile or FuselageProfile()

    def design_fuselage(self, requirements: FuselageRequirements) -> FuselageResult:
        """
        Orchestrates fuselage sizing and internal packaging layout calculations.

        Args:
            requirements (FuselageRequirements): inputs.

        Returns:
            FuselageResult: Sized fuselage system.
        """
        mission_res = requirements.mission_result
        config_res = requirements.configuration_result
        wing_res = requirements.wing_result
        tail_res = requirements.tail_result

        # 1. Strategy selection
        strategy = VTOLFuselageStrategyRegistry.get(mission_res.mission_profile.mission_category)

        # 2. Sizing Geometry
        mtow = mission_res.mission_analysis.estimated_mtow_kg
        f_type = requirements.preferred_fuselage_type or strategy.default_fuselage_type

        # Sized dimensions scaling with MTOW
        length = requirements.preferred_length_m or round((mtow * 0.35) ** 0.33 * 1.15, 3)
        width = requirements.preferred_width_m or round(length * 0.14, 3)
        height = requirements.preferred_height_m or round(length * 0.17, 3)

        shape = strategy.default_shape
        # Cambered box correction factors
        vol = length * width * height * 0.72
        front_area = width * height * 0.82
        wet_area = length * (width + height) * 2.0 * 0.76

        geom = FuselageGeometry(
            fuselage_type=f_type,
            length_m=length,
            width_m=width,
            height_m=height,
            cross_section_shape=shape,
            volume_m3=round(vol, 5),
            wetted_area_m2=round(wet_area, 3),
            frontal_area_m2=round(front_area, 4),
        )

        # 3. Compartment Layout segmenting
        shares = strategy.get_compartment_shares()
        bulkhead_positions = [0.0]
        accumulated_len = 0.0

        b_vol = vol * shares["battery"]
        b_len = length * shares["battery"]
        b_pos_x = b_len / 2.0
        accumulated_len += b_len
        bulkhead_positions.append(round(accumulated_len, 3))

        p_vol = vol * shares["payload"]
        p_len = length * shares["payload"]
        p_pos_x = accumulated_len + p_len / 2.0
        accumulated_len += p_len
        bulkhead_positions.append(round(accumulated_len, 3))

        a_vol = vol * shares["avionics"]
        a_len = length * shares["avionics"]
        a_pos_x = accumulated_len + a_len / 2.0
        accumulated_len += a_len
        bulkhead_positions.append(round(accumulated_len, 3))

        comp_layout = CompartmentLayout(
            battery_bay=Compartment(
                name="Battery Compartment",
                volume_m3=round(b_vol, 5),
                length_m=round(b_len, 3),
                width_m=round(width * 0.9, 3),
                height_m=round(height * 0.9, 3),
                position_x_m=round(b_pos_x, 3),
                is_accessible=True,
            ),
            payload_bay=Compartment(
                name="Payload Compartment",
                volume_m3=round(p_vol, 5),
                length_m=round(p_len, 3),
                width_m=round(width * 0.9, 3),
                height_m=round(height * 0.9, 3),
                position_x_m=round(p_pos_x, 3),
                is_accessible=True,
            ),
            avionics_bay=Compartment(
                name="Avionics Compartment",
                volume_m3=round(a_vol, 5),
                length_m=round(a_len, 3),
                width_m=round(width * 0.9, 3),
                height_m=round(height * 0.9, 3),
                position_x_m=round(a_pos_x, 3),
                is_accessible=True,
            ),
            metadata={"bulkhead_x_locations": bulkhead_positions},
        )

        # 4. Sizing Structural Shell Weight
        t_skin = self._profile.default_skin_thickness_mm
        density = self._profile.composite_density_kg_m3
        # structural weight = skin volume * density
        struct_weight = wet_area * t_skin * 0.001 * density

        reinforcements = ["wing_attachment_bulkhead"]
        if config_res.selected_configuration == VTOLType.TWIN_BOOM_VTOL:
            reinforcements.append("boom_sleeve_bulkheads")
        if mtow > 15.0:
            reinforcements.append("landing_gear_mount_stiffeners")

        structure = FuselageStructure(
            construction_type="Composite Sandwich Monocoque" if mtow > 10.0 else "Ribbed Balsa Carbon-reinforcement",
            estimated_fuselage_weight_kg=round(struct_weight, 3),
            wall_thickness_mm=t_skin,
            reinforcement_locations=reinforcements,
            crash_energy_absorption_level="High" if strategy.category == "Cargo" else "Medium",
        )

        # 5. Place Subsystems & CG Accommodation
        # Estimate subsystem masses
        bat_mass = round(mission_res.mission_profile.total_energy_demand_kwh * 4.4, 2)
        payload_mass = mission_res.mission_profile.payload_kg
        avionics_mass = 0.85

        # Position layout centroids relative to nose
        # Place Wing Main Spar joint at 45% of fuselage length
        wing_joint_x = length * 0.45

        # Place Payload forward
        pay_x = wing_joint_x - length * 0.22
        # Place Avionics aft
        av_x = wing_joint_x + length * 0.18
        # Fuselage structural weight centroid at 50% length
        struct_x = length * 0.50

        # Dynamically size battery placement offset to balance nose-heavy payload
        dx_pay = pay_x - wing_joint_x
        dx_avi = av_x - wing_joint_x
        dx_struct = struct_x - wing_joint_x

        needed_dx_bat = -(payload_mass * dx_pay + avionics_mass * dx_avi + struct_weight * dx_struct) / max(0.1, bat_mass)
        max_bat_offset = length * 0.40
        bat_offset = max(-max_bat_offset, min(max_bat_offset, needed_dx_bat))
        bat_x = wing_joint_x + bat_offset

        placements = [
            SubsystemPlacement("Battery Pack", round(bat_x, 3), 0.0, 0.0, bat_mass, round(b_vol * 0.7, 5)),
            SubsystemPlacement("Payload Sensor", round(pay_x, 3), 0.0, 0.0, payload_mass, round(p_vol * 0.6, 5)),
            SubsystemPlacement("Avionics autopilot", round(av_x, 3), 0.0, 0.0, avionics_mass, round(a_vol * 0.4, 5)),
            SubsystemPlacement("Structural Shell", round(struct_x, 3), 0.0, 0.0, round(struct_weight, 3), 0.0),
        ]

        total_mass = bat_mass + payload_mass + avionics_mass + struct_weight
        sum_moments = (bat_mass * bat_x) + (payload_mass * pay_x) + (avionics_mass * av_x) + (struct_weight * struct_x)
        cg_x = sum_moments / total_mass

        # Sizing CG Offset relative to Wing MAC
        # Sized MAC parameters from wing geometry
        wing_geom = wing_res.wing_geometry
        taper = wing_geom.taper_ratio
        mac = wing_geom.root_chord_m * (2.0 / 3.0) * ((1.0 + taper + taper**2) / (1.0 + taper))

        # We assume wing leading edge aligns at `wing_joint_x - 0.25 * mac` (25% MAC placement)
        wing_le_x = wing_joint_x - 0.25 * mac
        # Offset distance from 25% MAC neutral point
        cg_offset_m = cg_x - (wing_le_x + 0.25 * mac)
        cg_offset_percent = (cg_offset_m / mac) * 100.0

        # Packaging efficiency = occupied volume / available volume
        total_occupied_vol = sum(p.volume_m3 for p in placements)
        pkg_eff = (total_occupied_vol / vol) * 100.0

        internal_layout = InternalLayout(
            placements=placements,
            packaging_efficiency=round(pkg_eff, 1),
            center_of_gravity_x_m=round(cg_x, 3),
        )

        # 6. Sizing Mounting Interfaces
        wing_interface = MountingInterface(
            name="Main Wing Box Attachment",
            type="Dual-bolt Aluminum Clevis",
            location_x_m=round(wing_joint_x, 3),
            location_y_m=0.0,
            location_z_m=round(height * 0.5, 3),
            bolt_circle_diameter_mm=12.0,
            load_limit_n=round(mtow * 9.80665 * 6.5, 1),
        )

        tail_interface = None
        if tail_res.tail_geometry.horizontal_area_m2 > 0:
            tail_interface = MountingInterface(
                name="Tail Boom Fuselage Socket",
                type="Internal Carbon Joint Sleeve",
                location_x_m=round(length, 3),
                location_y_m=0.0,
                location_z_m=0.0,
                bolt_circle_diameter_mm=16.0,
                load_limit_n=round(mtow * 9.80665 * 3.5, 1),
            )

        mounts = MountingInterfaces(
            wing_attachment=wing_interface,
            tail_attachment=tail_interface,
        )

        # 7. Sizing Cooling Layout
        inlet_area = 6.0 + bat_mass * 1.2
        cooling = CoolingLayout(
            inlets=[
                CoolingInlet("Battery Intake Scope", round(inlet_area, 1), round(b_pos_x - 0.1, 3), 0.015),
                CoolingInlet("Avionics NACA Vent", 5.0, round(a_pos_x - 0.05, 3), 0.005),
            ],
            has_active_cooling=bat_mass > 8.0,  # heavy battery requires cooling fans during static hover
            estimated_cooling_effectiveness=82.0,
        )

        # 8. Sizing Landing Gear Interfaces
        gear_type = "Skids" if config_res.selected_configuration == VTOLType.TAIL_SITTER else "Tricycle Wheels"
        gear_att = [
            GearAttachmentPoint("Nose Gear Hardpoint", round(length * 0.15, 3), 0.0, round(-height * 0.5, 3), True),
            GearAttachmentPoint("Main Gear Left", round(wing_joint_x + 0.1, 3), round(-width * 0.8, 3), round(-height * 0.5, 3), True),
            GearAttachmentPoint("Main Gear Right", round(wing_joint_x + 0.1, 3), round(width * 0.8, 3), round(-height * 0.5, 3), True),
        ]
        gear_interfaces = LandingGearInterfaces(
            attachment_points=gear_att,
            landing_gear_type=gear_type,
            track_width_m=round(width * 1.6, 2),
            wheelbase_m=round(wing_joint_x - length * 0.15 + 0.1, 2),
        )

        # 9. Sizing Boom Interfaces
        boom_att: List[BoomAttachmentPoint] = []
        if config_res.selected_configuration in (VTOLType.QUADPLANE, VTOLType.LIFT_CRUISE, VTOLType.TWIN_BOOM_VTOL):
            boom_att.extend([
                BoomAttachmentPoint("Front Left Boom Mount", round(wing_joint_x - 0.2, 3), round(-width * 0.5, 3), 0.0, "Clamping Ring Collar"),
                BoomAttachmentPoint("Front Right Boom Mount", round(wing_joint_x - 0.2, 3), round(width * 0.5, 3), 0.0, "Clamping Ring Collar"),
                BoomAttachmentPoint("Rear Left Boom Mount", round(wing_joint_x + 0.3, 3), round(-width * 0.5, 3), 0.0, "Clamping Ring Collar"),
                BoomAttachmentPoint("Rear Right Boom Mount", round(wing_joint_x + 0.3, 3), round(width * 0.5, 3), 0.0, "Clamping Ring Collar"),
            ])

        boom_diam = tail_res.tail_structure.boom_diameter_mm
        boom_interfaces = BoomInterfaces(
            attachment_points=boom_att,
            number_of_booms=len(boom_att),
            boom_diameter_mm=boom_diam,
        )

        # 10. Performance analysis trade-offs
        # Aerodynamic bare drag coefficient based on shape
        if shape == "Circular":
            cd0_bare = self._profile.reference_drag_coefficient_cd0
        elif shape == "Oval":
            cd0_bare = self._profile.reference_drag_coefficient_cd0 * 1.2
        else:
            cd0_bare = self._profile.reference_drag_coefficient_cd0 * 1.5

        # Sized drag coefficient normalized by wing area
        cd0_fuse = cd0_bare * (front_area / wing_res.wing_geometry.area_m2)

        analysis = FuselageAnalysis(
            structural_efficiency=85.0 if f_type == "Monocoque" else 75.0,
            packaging_efficiency=round(pkg_eff, 1),
            aerodynamic_drag_coefficient_cd0=round(cd0_fuse, 5),
            cg_offset_from_wing_mac_percent=round(cg_offset_percent, 2),
            cooling_effectiveness_score=cooling.estimated_cooling_effectiveness,
            maintenance_accessibility_score=85.0 if shape == "Rectangular" else 75.0,
            manufacturability_score=80.0 if shape == "Rectangular" else 70.0,
            modularity_score=90.0 if f_type == "Modular" else 65.0,
            weight_efficiency=round((1.0 - (struct_weight / mtow)) * 100.0, 1),
        )

        # 11. Assemble notes, recommendations, and warnings
        notes = [
            f"Fuselage length sized: {geom.length_m:.3f} m.",
            f"Fuselage total internal packing volume: {geom.volume_m3:.5f} m³.",
            f"Calculated center-of-gravity location: {internal_layout.center_of_gravity_x_m:.3f} m from nose.",
        ]

        recs = strategy.get_recommendations()
        warnings: List[str] = []

        if analysis.packaging_efficiency > 75.0:
            warnings.append(f"High packaging density ({analysis.packaging_efficiency:.1f}%). Heat build-up hazard.")
        if cooling.has_active_cooling:
            notes.append("Active fan cooling sized for the battery compartment during hover segments.")

        result = FuselageResult(
            fuselage_geometry=geom,
            structural_layout=structure,
            internal_layout=internal_layout,
            compartment_layout=comp_layout,
            mounting_interfaces=mounts,
            cooling_layout=cooling,
            engineering_analysis=analysis,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
            metadata={
                "landing_gear": gear_interfaces,
                "booms": boom_interfaces,
            },
        )

        # 12. Run validators (raises error if invalid)
        self._validator.validate(requirements, result)

        meta = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.__class__.__name__,
        }
        result.metadata.update(meta)

        return result
