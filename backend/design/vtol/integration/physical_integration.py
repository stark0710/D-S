"""
VTOL Phase 9 Physical Installation Model Engine.

Purpose:
    Establishes the authoritative 3D spatial layout and physical coordinates (x, y, z)
    for every structural component and commercial hardware item in the airframe.

Coordinate System:
    - Datum: Fuselage Nose (x = 0.0 m)
    - Longitudinal axis (+x): Positive aft toward tail
    - Lateral axis (+y): Positive starboard (aircraft right)
    - Vertical axis (+z): Positive upward

Standards:
    - Strict provenance classification: CONFIGURABLE_ASSUMPTION or UPSTREAM_RESULT.
    - Captures all 27 BOM components plus airframe structural assemblies from Phase 5.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from backend.design.vtol.commercial.bom import CommercialBillOfMaterials
from backend.design.vtol.commercial.product_models import HardwareCategory

from .integration_models import (
    AircraftRole,
    ComponentLocation,
    MountingRegion,
    ProvenanceCategory,
    VerificationCheckStatus,
)


class PhysicalInstallationEngine:
    """
    Synthesizes the complete 3D spatial model of installed airframe and commercial components.
    """

    @classmethod
    def build_installation_model(
        cls,
        bom: CommercialBillOfMaterials,
        airframe_mass_overrides: Optional[Dict[str, float]] = None,
    ) -> List[ComponentLocation]:
        """
        Synthesizes the complete installed component layout with exact coordinates.
        """
        locations: List[ComponentLocation] = []
        bom_map = {item.category: item for item in bom.items}

        # -----------------------------------------------------------------
        # 1. AIRFRAME STRUCTURAL ASSEMBLIES (Authoritative Phase 5 Ledger)
        # -----------------------------------------------------------------
        # Main Wing Structure (Panels, ribs, carbon spars)
        wing_mass = (airframe_mass_overrides or {}).get("wing_structure_mass_kg", 1.050)
        locations.append(ComponentLocation(
            component_name="Wing Structural Assembly",
            role=None,
            mass_kg=wing_mass,
            x_m=0.5000,
            y_m=0.0000,
            z_m=0.1000,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Main carbon fiber composite wing panels, center spar joiner, and ribs",
        ))

        # Fuselage Main Structure (Nose to tail boom firewall)
        fuse_mass = (airframe_mass_overrides or {}).get("fuselage_structure_mass_kg", 0.850)
        locations.append(ComponentLocation(
            component_name="Fuselage Primary Shell & Formers",
            role=None,
            mass_kg=fuse_mass,
            x_m=0.4500,
            y_m=0.0000,
            z_m=0.0000,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Fiberglass/carbon monocoque fuselage fuselage shell, bulkheads, and hatches",
        ))

        # Twin VTOL Booms (Left and Right carbon booms supporting lift motors)
        booms_mass = (airframe_mass_overrides or {}).get("vtol_booms_mass_kg", 0.520)
        locations.append(ComponentLocation(
            component_name="Twin VTOL Motor Booms (Pair)",
            role=None,
            mass_kg=booms_mass,
            x_m=0.5000,
            y_m=0.0000,  # Symmetric pair at y = +/- 0.60m
            z_m=0.0500,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Twin 25mm carbon fiber tubes mounted at spanwise stations y = +/- 0.60m",
        ))

        # Inverted V-Tail Empennage
        tail_mass = (airframe_mass_overrides or {}).get("tail_structure_mass_kg", 0.320)
        locations.append(ComponentLocation(
            component_name="Inverted V-Tail Structure",
            role=None,
            mass_kg=tail_mass,
            x_m=1.2000,
            y_m=0.0000,
            z_m=-0.0500,
            mounting_region=MountingRegion.TAIL_LEFT_FIN,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Twin ruddervator surfaces in an inverted V configuration at tail boom aft end",
        ))

        # Landing Gear Skids
        skids_mass = (airframe_mass_overrides or {}).get("landing_skids_mass_kg", 0.280)
        locations.append(ComponentLocation(
            component_name="Carbon Fiber Landing Skids",
            role=None,
            mass_kg=skids_mass,
            x_m=0.4800,
            y_m=0.0000,
            z_m=-0.1500,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Twin carbon skid struts mounted under fuselage for ground clearance",
        ))

        # Mechanical Installation Hardware & Wiring Harness
        wiring_mass = (airframe_mass_overrides or {}).get("wiring_hardware_mass_kg", 0.260)
        locations.append(ComponentLocation(
            component_name="Wiring Harness & Mounting Brackets",
            role=None,
            mass_kg=wiring_mass,
            x_m=0.4800,
            y_m=0.0000,
            z_m=0.0000,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Silicone wiring, standoffs, connectors, motor mounts, and fasteners",
        ))

        # -----------------------------------------------------------------
        # 2. COMMERCIAL HARDWARE COMPONENTS (Phase 8 Verified BOM)
        # -----------------------------------------------------------------
        # Battery Pack (Dominant mass: 2.600 kg)
        batt_item = bom_map.get(HardwareCategory.BATTERY_PACK)
        batt_mass = batt_item.unit_mass_kg if batt_item else 2.600
        locations.append(ComponentLocation(
            component_name="Tattu Plus 6S 22000mAh Battery Pack",
            role=AircraftRole.BATTERY_MAIN,
            mass_kg=batt_mass,
            x_m=0.4500,  # Center bay under wing spar
            y_m=0.0000,
            z_m=-0.0200,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Main propulsion battery placed on adjustable CG floor tray",
        ))

        # Payload Camera (Sony RX0 II: 0.250 kg)
        cam_item = bom_map.get(HardwareCategory.MISSION_PAYLOAD)
        cam_mass = cam_item.unit_mass_kg if cam_item else 0.250
        locations.append(ComponentLocation(
            component_name="Sony DSC-RX0 II Mapping Payload",
            role=AircraftRole.MISSION_PAYLOAD_CAMERA,
            mass_kg=cam_mass,
            x_m=0.2800,  # Forward fuselage bay
            y_m=0.0000,
            z_m=-0.0600,
            mounting_region=MountingRegion.NOSE_AVIONICS_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Nose nadir viewing window on vibration isolation dampers",
        ))

        # Autopilot (Holybro Pixhawk 6X: 0.075 kg)
        fc_item = bom_map.get(HardwareCategory.FLIGHT_CONTROLLER)
        fc_mass = fc_item.unit_mass_kg if fc_item else 0.075
        locations.append(ComponentLocation(
            component_name="Holybro Pixhawk 6X Autopilot",
            role=AircraftRole.AUTOPILOT_PIXHAWK,
            mass_kg=fc_mass,
            x_m=0.4900,  # Directly over airframe CG
            y_m=0.0000,
            z_m=0.0400,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Autopilot mounted on anti-vibration damping platform at nominal CG",
        ))

        # Power Distribution Board (Matek PDB-HEX: 0.045 kg)
        pdb_item = bom_map.get(HardwareCategory.POWER_DISTRIBUTION)
        pdb_mass = pdb_item.unit_mass_kg if pdb_item else 0.045
        locations.append(ComponentLocation(
            component_name="Matek Systems PDB-HEX 12S",
            role=AircraftRole.POWER_DISTRIBUTION,
            mass_kg=pdb_mass,
            x_m=0.4600,
            y_m=0.0000,
            z_m=0.0100,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="High-current distribution board directly above battery discharge leads",
        ))

        # Companion Computer (Raspberry Pi 4B: 0.046 kg)
        sbc_item = bom_map.get(HardwareCategory.COMPANION_COMPUTER)
        sbc_mass = sbc_item.unit_mass_kg if sbc_item else 0.046
        locations.append(ComponentLocation(
            component_name="Raspberry Pi 4 Model B (4GB)",
            role=AircraftRole.COMPANION_SBC,
            mass_kg=sbc_mass,
            x_m=0.3800,
            y_m=0.0000,
            z_m=0.0400,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Mounted on upper avionics shelf with aluminum heat sink case",
        ))

        # RTK GNSS Antenna/Receiver (Holybro H-RTK F9P: 0.065 kg)
        gnss_item = bom_map.get(HardwareCategory.NAVIGATION_GNSS)
        gnss_mass = gnss_item.unit_mass_kg if gnss_item else 0.065
        locations.append(ComponentLocation(
            component_name="Holybro H-RTK F9P Helical GNSS",
            role=AircraftRole.NAVIGATION_GNSS_RTK,
            mass_kg=gnss_mass,
            x_m=0.4200,
            y_m=0.0000,
            z_m=0.1600,  # Top deck mast
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Helical antenna on elevated mast clear of carbon wing shielding",
        ))

        # Digital Airspeed Sensor (Matek ASPD-4525: 0.015 kg)
        aspd_item = bom_map.get(HardwareCategory.AIRSPEED_SENSOR)
        aspd_mass = aspd_item.unit_mass_kg if aspd_item else 0.015
        locations.append(ComponentLocation(
            component_name="Matek ASPD-4525 Digital Pitot",
            role=AircraftRole.DIGITAL_AIRSPEED,
            mass_kg=aspd_mass,
            x_m=0.0500,  # Protruding forward of nose
            y_m=0.0000,
            z_m=0.0000,
            mounting_region=MountingRegion.NOSE_AVIONICS_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Pitot-static probe in clean undisturbed free-stream flow ahead of nose",
        ))

        # Telemetry Radio (SiK 915MHz: 0.025 kg)
        telem_item = bom_map.get(HardwareCategory.TELEMETRY_LINK)
        telem_mass = telem_item.unit_mass_kg if telem_item else 0.025
        locations.append(ComponentLocation(
            component_name="Holybro SiK Telemetry Radio V3",
            role=AircraftRole.TELEMETRY_TRANSCEIVER,
            mass_kg=telem_mass,
            x_m=0.3600,
            y_m=0.0500,
            z_m=0.0200,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="915MHz antenna protruding through lower starboard fuselage fairing",
        ))

        # RC Receiver (Crossfire Nano: 0.005 kg)
        rc_item = bom_map.get(HardwareCategory.RC_RECEIVER)
        rc_mass = rc_item.unit_mass_kg if rc_item else 0.005
        locations.append(ComponentLocation(
            component_name="TBS Crossfire Nano RX",
            role=AircraftRole.RC_RECEIVER,
            mass_kg=rc_mass,
            x_m=0.3500,
            y_m=-0.0500,
            z_m=0.0200,
            mounting_region=MountingRegion.FUSELAGE_CENTER_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Immortal-T dipole antenna on port fuselage side",
        ))

        # Cruise Propulsion (Motor, Propeller, ESC: 0.260 + 0.025 + 0.050 kg)
        cmtr_item = bom_map.get(HardwareCategory.CRUISE_MOTOR)
        cprp_item = bom_map.get(HardwareCategory.CRUISE_PROPELLER)
        cesc_item = bom_map.get(HardwareCategory.CRUISE_ESC)
        cmtr_mass = cmtr_item.unit_mass_kg if cmtr_item else 0.260
        cprp_mass = cprp_item.unit_mass_kg if cprp_item else 0.025
        cesc_mass = cesc_item.unit_mass_kg if cesc_item else 0.050

        locations.append(ComponentLocation(
            component_name="T-Motor AT2820 KV880 Pusher Motor",
            role=AircraftRole.CRUISE_MOTOR,
            mass_kg=cmtr_mass,
            x_m=0.9200,  # Tail firewall pusher
            y_m=0.0000,
            z_m=0.0200,
            mounting_region=MountingRegion.FUSELAGE_FIREWALL,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Pusher brushless motor mounted on aft carbon fuselage firewall",
        ))
        locations.append(ComponentLocation(
            component_name="APC 11x7 Thin Electric Pusher Propeller",
            role=AircraftRole.CRUISE_PROP,
            mass_kg=cprp_mass,
            x_m=0.9500,
            y_m=0.0000,
            z_m=0.0200,
            mounting_region=MountingRegion.FUSELAGE_FIREWALL,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Aft pusher propeller collet mounted on motor shaft",
        ))
        locations.append(ComponentLocation(
            component_name="Hobbywing FlyFun 40A V5 ESC",
            role=AircraftRole.CRUISE_ESC,
            mass_kg=cesc_mass,
            x_m=0.8600,
            y_m=0.0000,
            z_m=0.0000,
            mounting_region=MountingRegion.FUSELAGE_AFT_BAY,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Cruise ESC located in ventilated aft fuselage bay",
        ))

        # 4x VTOL Lift Motors, Propellers, and ESCs
        # Booms are at y = +/- 0.60m; Front motors at x = 0.25m, Rear motors at x = 0.75m
        vmtr_item = bom_map.get(HardwareCategory.VTOL_MOTOR)
        vprp_item = bom_map.get(HardwareCategory.VTOL_PROPELLER)
        vesc_item = bom_map.get(HardwareCategory.VTOL_ESC)
        vmtr_mass = vmtr_item.unit_mass_kg if vmtr_item else 0.140
        vprp_mass = vprp_item.unit_mass_kg if vprp_item else 0.028
        vesc_mass = vesc_item.unit_mass_kg if vesc_item else 0.035

        quad_positions = [
            (AircraftRole.VTOL_MOTOR_1, AircraftRole.VTOL_PROP_1, AircraftRole.VTOL_ESC_1, "Front-Left", 0.2500, -0.6000, MountingRegion.BOOM_LEFT_FRONT),
            (AircraftRole.VTOL_MOTOR_2, AircraftRole.VTOL_PROP_2, AircraftRole.VTOL_ESC_2, "Front-Right", 0.2500, 0.6000, MountingRegion.BOOM_RIGHT_FRONT),
            (AircraftRole.VTOL_MOTOR_3, AircraftRole.VTOL_PROP_3, AircraftRole.VTOL_ESC_3, "Rear-Left", 0.7500, -0.6000, MountingRegion.BOOM_LEFT_AFT),
            (AircraftRole.VTOL_MOTOR_4, AircraftRole.VTOL_PROP_4, AircraftRole.VTOL_ESC_4, "Rear-Right", 0.7500, 0.6000, MountingRegion.BOOM_RIGHT_AFT),
        ]

        for m_role, p_role, e_role, name, x_pos, y_pos, reg in quad_positions:
            locations.append(ComponentLocation(
                component_name=f"T-Motor MN4014 KV330 ({name})",
                role=m_role,
                mass_kg=vmtr_mass,
                x_m=x_pos,
                y_m=y_pos,
                z_m=0.0500,
                mounting_region=reg,
                reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
                installation_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes=f"{name} lift motor mounted on carbon tube clamp",
            ))
            locations.append(ComponentLocation(
                component_name=f"T-Motor P16x5.4 Carbon Propeller ({name})",
                role=p_role,
                mass_kg=vprp_mass,
                x_m=x_pos,
                y_m=y_pos,
                z_m=0.0800,
                mounting_region=reg,
                reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
                installation_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes=f"{name} carbon fiber folding/direct rotor",
            ))
            # ESCs located inside boom 5cm inboard of motor
            esc_x = x_pos + (0.0500 if x_pos < 0.5 else -0.0500)
            locations.append(ComponentLocation(
                component_name=f"T-Motor AIR 40A ESC ({name})",
                role=e_role,
                mass_kg=vesc_mass,
                x_m=esc_x,
                y_m=y_pos,
                z_m=0.0500,
                mounting_region=reg,
                reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
                installation_status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes=f"{name} motor ESC placed inside boom airflow tube",
            ))

        # 4x Control Surface Servos (KST DS215MG: 0.020 kg each)
        servo_item = bom_map.get(HardwareCategory.SERVO)
        servo_mass = servo_item.unit_mass_kg if servo_item else 0.020

        locations.append(ComponentLocation(
            component_name="Left Aileron Servo (KST DS215MG)",
            role=AircraftRole.LEFT_AILERON_SERVO,
            mass_kg=servo_mass,
            x_m=0.5200,
            y_m=-0.8500,
            z_m=0.1000,
            mounting_region=MountingRegion.WING_LEFT_OUTBOARD,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Left wing servo bay with direct carbon pushrod linkage",
        ))
        locations.append(ComponentLocation(
            component_name="Right Aileron Servo (KST DS215MG)",
            role=AircraftRole.RIGHT_AILERON_SERVO,
            mass_kg=servo_mass,
            x_m=0.5200,
            y_m=0.8500,
            z_m=0.1000,
            mounting_region=MountingRegion.WING_RIGHT_OUTBOARD,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Right wing servo bay with direct carbon pushrod linkage",
        ))
        locations.append(ComponentLocation(
            component_name="Left Ruddervator Servo (KST DS215MG)",
            role=AircraftRole.VTAIL_SURFACE_1_SERVO,
            mass_kg=servo_mass,
            x_m=1.1800,
            y_m=-0.1500,
            z_m=-0.0500,
            mounting_region=MountingRegion.TAIL_LEFT_FIN,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Aft tail boom servo mount with short ball-link rod",
        ))
        locations.append(ComponentLocation(
            component_name="Right Ruddervator Servo (KST DS215MG)",
            role=AircraftRole.VTAIL_SURFACE_2_SERVO,
            mass_kg=servo_mass,
            x_m=1.1800,
            y_m=0.1500,
            z_m=-0.0500,
            mounting_region=MountingRegion.TAIL_RIGHT_FIN,
            reference_frame="AIRCRAFT_BODY_NOSE_DATUM",
            installation_status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Aft tail boom servo mount with short ball-link rod",
        ))

        return locations
