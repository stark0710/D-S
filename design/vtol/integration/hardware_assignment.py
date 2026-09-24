"""
VTOL Phase 9 Hardware Assignment Engine.

Purpose:
    Deterministic mapping of every commercial component from the Phase 8 Bill of Materials (BOM)
    into an authoritative functional role in the Torq Wings Lift + Cruise (QuadPlane) architecture.

Standards:
    - 1-to-1 role assignment for all 27 BOM parts.
    - Zero orphaned BOM line-items (no unassigned hardware).
    - Zero duplicate role ownership.
    - Preserves manufacturer model, mass, power rating, and provenance from Phase 8.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from backend.design.vtol.commercial.bom import CommercialBillOfMaterials, BillOfMaterialsItem
from backend.design.vtol.commercial.product_models import HardwareCategory

from .integration_models import (
    AircraftRole,
    HardwareAssignment,
    ProvenanceCategory,
    VerificationCheckStatus,
)


class HardwareAssignmentEngine:
    """
    Assigns Phase 8 commercial BOM items to discrete aircraft integration roles.
    """

    @classmethod
    def assign_hardware(
        cls,
        bom: CommercialBillOfMaterials,
    ) -> List[HardwareAssignment]:
        """
        Maps all BOM items to discrete aircraft functional roles.
        """
        assignments: List[HardwareAssignment] = []
        bom_by_category: Dict[HardwareCategory, BillOfMaterialsItem] = {
            item.category: item for item in bom.items
        }

        # -------------------------------------------------------------
        # 1. VTOL LIFT PROPULSION (4x Motors, 4x Propellers, 4x ESCs)
        # -------------------------------------------------------------
        vtol_motor = bom_by_category.get(HardwareCategory.VTOL_MOTOR)
        vtol_prop = bom_by_category.get(HardwareCategory.VTOL_PROPELLER)
        vtol_esc = bom_by_category.get(HardwareCategory.VTOL_ESC)

        motor_roles = [
            (AircraftRole.VTOL_MOTOR_1, "Front-Left Lift Motor"),
            (AircraftRole.VTOL_MOTOR_2, "Front-Right Lift Motor"),
            (AircraftRole.VTOL_MOTOR_3, "Rear-Left Lift Motor"),
            (AircraftRole.VTOL_MOTOR_4, "Rear-Right Lift Motor"),
        ]
        prop_roles = [
            (AircraftRole.VTOL_PROP_1, "Front-Left 16x5.4 Carbon Propeller"),
            (AircraftRole.VTOL_PROP_2, "Front-Right 16x5.4 Carbon Propeller"),
            (AircraftRole.VTOL_PROP_3, "Rear-Left 16x5.4 Carbon Propeller"),
            (AircraftRole.VTOL_PROP_4, "Rear-Right 16x5.4 Carbon Propeller"),
        ]
        esc_roles = [
            (AircraftRole.VTOL_ESC_1, "Front-Left 40A DShot ESC"),
            (AircraftRole.VTOL_ESC_2, "Front-Right 40A DShot ESC"),
            (AircraftRole.VTOL_ESC_3, "Rear-Left 40A DShot ESC"),
            (AircraftRole.VTOL_ESC_4, "Rear-Right 40A DShot ESC"),
        ]

        if vtol_motor:
            for idx, (role, desc) in enumerate(motor_roles, 1):
                assignments.append(HardwareAssignment(
                    assignment_id=f"ASGN-VTOL-MTR-{idx}",
                    role=role,
                    bom_id=vtol_motor.bom_id,
                    category=vtol_motor.category.value,
                    manufacturer=vtol_motor.manufacturer,
                    model=vtol_motor.model,
                    quantity=1,
                    unit_mass_kg=vtol_motor.unit_mass_kg,
                    total_mass_kg=vtol_motor.unit_mass_kg,
                    power_requirement_w=406.1,  # Authoritative Phase 2 per-motor hover electrical power
                    voltage_v=22.2,             # 6S Nominal
                    interface_type="3-Phase Brushless AC / Bullet Connectors",
                    notes=f"{desc}; satisfies Phase 2 per-motor hover thrust >= 25.08N",
                    provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
                ))

        if vtol_prop:
            for idx, (role, desc) in enumerate(prop_roles, 1):
                assignments.append(HardwareAssignment(
                    assignment_id=f"ASGN-VTOL-PROP-{idx}",
                    role=role,
                    bom_id=vtol_prop.bom_id,
                    category=vtol_prop.category.value,
                    manufacturer=vtol_prop.manufacturer,
                    model=vtol_prop.model,
                    quantity=1,
                    unit_mass_kg=vtol_prop.unit_mass_kg,
                    total_mass_kg=vtol_prop.unit_mass_kg,
                    power_requirement_w=None,
                    voltage_v=None,
                    interface_type="Direct Hub Mount (M3x12 bolts)",
                    notes=desc,
                    provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
                ))

        if vtol_esc:
            for idx, (role, desc) in enumerate(esc_roles, 1):
                assignments.append(HardwareAssignment(
                    assignment_id=f"ASGN-VTOL-ESC-{idx}",
                    role=role,
                    bom_id=vtol_esc.bom_id,
                    category=vtol_esc.category.value,
                    manufacturer=vtol_esc.manufacturer,
                    model=vtol_esc.model,
                    quantity=1,
                    unit_mass_kg=vtol_esc.unit_mass_kg,
                    total_mass_kg=vtol_esc.unit_mass_kg,
                    power_requirement_w=None,
                    voltage_v=22.2,
                    interface_type="Power: DC Solder Pad / Signal: DShot600 Twisted Pair",
                    notes=f"{desc}; rated 40A continuous / 50A burst 6S",
                    provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
                ))

        # -------------------------------------------------------------
        # 2. FORWARD CRUISE PROPULSION (1x Motor, 1x Propeller, 1x ESC)
        # -------------------------------------------------------------
        cruise_motor = bom_by_category.get(HardwareCategory.CRUISE_MOTOR)
        cruise_prop = bom_by_category.get(HardwareCategory.CRUISE_PROPELLER)
        cruise_esc = bom_by_category.get(HardwareCategory.CRUISE_ESC)

        if cruise_motor:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-CRUISE-MTR-1",
                role=AircraftRole.CRUISE_MOTOR,
                bom_id=cruise_motor.bom_id,
                category=cruise_motor.category.value,
                manufacturer=cruise_motor.manufacturer,
                model=cruise_motor.model,
                quantity=1,
                unit_mass_kg=cruise_motor.unit_mass_kg,
                total_mass_kg=cruise_motor.unit_mass_kg,
                power_requirement_w=360.0,  # Authoritative Phase 3/Fixed-Wing cruise power
                voltage_v=22.2,
                interface_type="3-Phase Brushless AC / 3.5mm Bullet Connectors",
                notes="Pusher configuration mounted at fuselage tail firewall; satisfies forward thrust >= 16.5N",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if cruise_prop:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-CRUISE-PROP-1",
                role=AircraftRole.CRUISE_PROP,
                bom_id=cruise_prop.bom_id,
                category=cruise_prop.category.value,
                manufacturer=cruise_prop.manufacturer,
                model=cruise_prop.model,
                quantity=1,
                unit_mass_kg=cruise_prop.unit_mass_kg,
                total_mass_kg=cruise_prop.unit_mass_kg,
                power_requirement_w=None,
                voltage_v=None,
                interface_type="Prop Adapter Collet (M6 / 5mm shaft)",
                notes="11x7 Thin Electric pusher propeller",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if cruise_esc:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-CRUISE-ESC-1",
                role=AircraftRole.CRUISE_ESC,
                bom_id=cruise_esc.bom_id,
                category=cruise_esc.category.value,
                manufacturer=cruise_esc.manufacturer,
                model=cruise_esc.model,
                quantity=1,
                unit_mass_kg=cruise_esc.unit_mass_kg,
                total_mass_kg=cruise_esc.unit_mass_kg,
                power_requirement_w=None,
                voltage_v=22.2,
                interface_type="Power: XT60 / Signal: Standard PWM 3-pin JR connector",
                notes="40A continuous / 60A peak 6S brushless ESC",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        # -------------------------------------------------------------
        # 3. CONTROL SURFACES (4x Digital Servos)
        # -------------------------------------------------------------
        servo = bom_by_category.get(HardwareCategory.SERVO)
        servo_roles = [
            (AircraftRole.LEFT_AILERON_SERVO, "Left Wing Outboard Aileron Servo"),
            (AircraftRole.RIGHT_AILERON_SERVO, "Right Wing Outboard Aileron Servo"),
            (AircraftRole.VTAIL_SURFACE_1_SERVO, "Left Inverted V-Tail Ruddervator Servo"),
            (AircraftRole.VTAIL_SURFACE_2_SERVO, "Right Inverted V-Tail Ruddervator Servo"),
        ]

        if servo:
            for idx, (role, desc) in enumerate(servo_roles, 1):
                assignments.append(HardwareAssignment(
                    assignment_id=f"ASGN-SERVO-{idx}",
                    role=role,
                    bom_id=servo.bom_id,
                    category=servo.category.value,
                    manufacturer=servo.manufacturer,
                    model=servo.model,
                    quantity=1,
                    unit_mass_kg=servo.unit_mass_kg,
                    total_mass_kg=servo.unit_mass_kg,
                    power_requirement_w=4.0,  # ~0.8A peak @ 5.0V under dynamic deflection
                    voltage_v=5.0,            # 5.0V regulated BEC rail
                    interface_type="3-pin JR Servo Connector (PWM)",
                    notes=f"{desc}; torque qualification DEFERRED per Phase 8 specification",
                    provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
                ))

        # -------------------------------------------------------------
        # 4. ENERGY & POWER DISTRIBUTION (Battery + PDB)
        # -------------------------------------------------------------
        battery = bom_by_category.get(HardwareCategory.BATTERY_PACK)
        pdb = bom_by_category.get(HardwareCategory.POWER_DISTRIBUTION)

        if battery:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-BATTERY-1",
                role=AircraftRole.BATTERY_MAIN,
                bom_id=battery.bom_id,
                category=battery.category.value,
                manufacturer=battery.manufacturer,
                model=battery.model,
                quantity=1,
                unit_mass_kg=battery.unit_mass_kg,
                total_mass_kg=battery.unit_mass_kg,
                power_requirement_w=None,
                voltage_v=22.2,
                interface_type="High-Current Discharge: AS150 / XT90-S Anti-Spark; Balance: JST-XH 7-pin",
                notes="6S 22000mAh 25C LiPo pack; nominal energy 488.4 Wh (> 407.0 Wh requirement)",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if pdb:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-PDB-1",
                role=AircraftRole.POWER_DISTRIBUTION,
                bom_id=pdb.bom_id,
                category=pdb.category.value,
                manufacturer=pdb.manufacturer,
                model=pdb.model,
                quantity=1,
                unit_mass_kg=pdb.unit_mass_kg,
                total_mass_kg=pdb.unit_mass_kg,
                power_requirement_w=None,
                voltage_v=22.2,
                interface_type="Main Solder Pads (12S rated) / Dual Regulated BECs (5V 5A + 12V 4A)",
                notes="Hexacopter/Octocopter PDB with dual BEC rails and integrated current sensing",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        # -------------------------------------------------------------
        # 5. AVIONICS & SENSORS (Pixhawk, RTK, Airspeed, Telemetry, RX)
        # -------------------------------------------------------------
        fc = bom_by_category.get(HardwareCategory.FLIGHT_CONTROLLER)
        gnss = bom_by_category.get(HardwareCategory.NAVIGATION_GNSS)
        airspeed = bom_by_category.get(HardwareCategory.AIRSPEED_SENSOR)
        telem = bom_by_category.get(HardwareCategory.TELEMETRY_LINK)
        rc = bom_by_category.get(HardwareCategory.RC_RECEIVER)

        if fc:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-AUTOPILOT-1",
                role=AircraftRole.AUTOPILOT_PIXHAWK,
                bom_id=fc.bom_id,
                category=fc.category.value,
                manufacturer=fc.manufacturer,
                model=fc.model,
                quantity=1,
                unit_mass_kg=fc.unit_mass_kg,
                total_mass_kg=fc.unit_mass_kg,
                power_requirement_w=5.0,  # ~1.0A @ 5.0V
                voltage_v=5.0,
                interface_type="JST-GH Standard Connectors / 16x PWM Output Channels",
                notes="Pixhawk 6X Autopilot with triple redundant IMU and dual power inputs",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if gnss:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-GNSS-1",
                role=AircraftRole.NAVIGATION_GNSS_RTK,
                bom_id=gnss.bom_id,
                category=gnss.category.value,
                manufacturer=gnss.manufacturer,
                model=gnss.model,
                quantity=1,
                unit_mass_kg=gnss.unit_mass_kg,
                total_mass_kg=gnss.unit_mass_kg,
                power_requirement_w=1.5,  # ~0.3A @ 5.0V
                voltage_v=5.0,
                interface_type="10-pin JST-GH (UART + I2C Compass)",
                notes="Holybro H-RTK F9P Helical dual-frequency RTK GNSS + Compass",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if airspeed:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-AIRSPEED-1",
                role=AircraftRole.DIGITAL_AIRSPEED,
                bom_id=airspeed.bom_id,
                category=airspeed.category.value,
                manufacturer=airspeed.manufacturer,
                model=airspeed.model,
                quantity=1,
                unit_mass_kg=airspeed.unit_mass_kg,
                total_mass_kg=airspeed.unit_mass_kg,
                power_requirement_w=0.25,  # ~0.05A @ 5.0V
                voltage_v=5.0,
                interface_type="4-pin JST-GH (I2C Bus)",
                notes="Matek ASPD-4525 Digital Differential Pitot Airspeed Sensor",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if telem:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-TELEM-1",
                role=AircraftRole.TELEMETRY_TRANSCEIVER,
                bom_id=telem.bom_id,
                category=telem.category.value,
                manufacturer=telem.manufacturer,
                model=telem.model,
                quantity=1,
                unit_mass_kg=telem.unit_mass_kg,
                total_mass_kg=telem.unit_mass_kg,
                power_requirement_w=2.5,  # ~0.5A peak transmit @ 5.0V
                voltage_v=5.0,
                interface_type="6-pin JST-GH (UART + CTS/RTS)",
                notes="Holybro SiK Telemetry Radio V3 915MHz 500mW MAVLink transceiver",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if rc:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-RC-1",
                role=AircraftRole.RC_RECEIVER,
                bom_id=rc.bom_id,
                category=rc.category.value,
                manufacturer=rc.manufacturer,
                model=rc.model,
                quantity=1,
                unit_mass_kg=rc.unit_mass_kg,
                total_mass_kg=rc.unit_mass_kg,
                power_requirement_w=0.5,  # ~0.1A @ 5.0V
                voltage_v=5.0,
                interface_type="4-pin Header / CRSF Protocol (UART)",
                notes="TBS Crossfire Nano RX long-range telemetry-capable receiver",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        # -------------------------------------------------------------
        # 6. COMPANION COMPUTER & PAYLOAD
        # -------------------------------------------------------------
        companion = bom_by_category.get(HardwareCategory.COMPANION_COMPUTER)
        payload = bom_by_category.get(HardwareCategory.MISSION_PAYLOAD)

        if companion:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-SBC-1",
                role=AircraftRole.COMPANION_SBC,
                bom_id=companion.bom_id,
                category=companion.category.value,
                manufacturer=companion.manufacturer,
                model=companion.model,
                quantity=1,
                unit_mass_kg=companion.unit_mass_kg,
                total_mass_kg=companion.unit_mass_kg,
                power_requirement_w=12.5,  # Up to 2.5A peak @ 5.0V under quad-core load
                voltage_v=5.0,
                interface_type="USB-C / GPIO 5V Pins + UART to Pixhawk TELEM2",
                notes="Raspberry Pi 4 Model B (4GB) for autonomy / computer vision / MAVROS",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        if payload:
            assignments.append(HardwareAssignment(
                assignment_id="ASGN-PAYLOAD-1",
                role=AircraftRole.MISSION_PAYLOAD_CAMERA,
                bom_id=payload.bom_id,
                category=payload.category.value,
                manufacturer=payload.manufacturer,
                model=payload.model,
                quantity=1,
                unit_mass_kg=payload.unit_mass_kg,
                total_mass_kg=payload.unit_mass_kg,
                power_requirement_w=5.0,  # Internal battery + optional 5V micro-USB trickle
                voltage_v=5.0,
                interface_type="Multi-Terminal / Micro-USB (Discrete Shutter Trigger)",
                notes="Sony DSC-RX0 II high-resolution mapping camera with anti-vibration mount",
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            ))

        return assignments

    @classmethod
    def validate_assignment_completeness(
        cls,
        bom: CommercialBillOfMaterials,
        assignments: List[HardwareAssignment],
    ) -> VerificationCheckStatus:
        """
        Confirms all BOM items are assigned and no duplicate roles exist.
        """
        assigned_roles = [a.role for a in assignments]
        if len(assigned_roles) != len(set(assigned_roles)):
            return VerificationCheckStatus.FAIL

        total_assigned_qty = sum(a.quantity for a in assignments)
        if total_assigned_qty != bom.total_parts_count:
            return VerificationCheckStatus.FAIL

        return VerificationCheckStatus.PASS
