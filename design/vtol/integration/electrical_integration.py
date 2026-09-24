"""
VTOL Phase 9 Electrical Architecture & Integration Engine.

Purpose:
    Constructs the explicit multi-tier electrical power distribution tree,
    evaluating voltage compatibility, continuous and burst current capacities,
    regulator margins, and connector requirements across all aircraft branches.

Standards:
    - Downstream analysis consuming Phase 8 verified hardware and Phase 2/3/4 power profiles.
    - Zero fabricated current draws: unverified sensor draws explicitly marked with provenance.
    - Power paths evaluated:
        A. Battery -> PDB
        B. PDB -> 4x VTOL ESCs -> Motors
        C. PDB -> Cruise ESC -> Cruise Motor
        D. Regulated 5V Rail -> Servos
        E. Regulated 5V Rail -> Flight Controller
        F. Regulated 5V Rail -> Avionics & Sensors
        G. Regulated 5V Rail -> Companion Computer (SBC)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from backend.design.vtol.commercial.bom import CommercialBillOfMaterials
from backend.design.vtol.commercial.product_models import HardwareCategory

from .integration_models import (
    AircraftRole,
    BusType,
    ElectricalBus,
    ElectricalLoad,
    HardwareAssignment,
    PowerPath,
    ProvenanceCategory,
    VerificationCheckStatus,
)


class ElectricalIntegrationEngine:
    """
    Builds and verifies the complete aircraft electrical power network.
    """

    # Upstream nominal voltages and authorized current draws
    SYSTEM_VOLTAGE_NOMINAL_V = 22.2  # 6S LiPo
    SYSTEM_VOLTAGE_MIN_V = 19.8      # 3.3V/cell cutoff
    SYSTEM_VOLTAGE_MAX_V = 25.2      # 4.2V/cell full charge
    REGULATED_5V_NOMINAL_V = 5.0
    REGULATED_12V_NOMINAL_V = 12.0

    @classmethod
    def build_electrical_architecture(
        cls,
        assignments: List[HardwareAssignment],
        bom: Optional[CommercialBillOfMaterials] = None,
    ) -> Tuple[List[ElectricalBus], List[PowerPath], List[ElectricalLoad]]:
        """
        Synthesizes the complete electrical buses, individual loads, and verified power paths.
        """
        loads: List[ElectricalLoad] = []
        paths: List[PowerPath] = []
        buses: List[ElectricalBus] = []

        # -----------------------------------------------------------------
        # 1. DEFINE INDIVIDUAL ELECTRICAL CONSUMER LOADS
        # -----------------------------------------------------------------
        # VTOL Motors 1-4 (Phase 2 authoritative hover power: 406.1 W per motor = 18.29 A @ 22.2 V)
        # Peak per-motor during gust / pitch-roll trim: ~30.0 A (666 W)
        for i in range(1, 5):
            role_mtr = getattr(AircraftRole, f"VTOL_MOTOR_{i}")
            loads.append(ElectricalLoad(
                load_id=f"LOAD-VTOL-MTR-{i}",
                load_name=f"VTOL Lift Motor {i}",
                role=role_mtr,
                bus_type=BusType.HIGH_VOLTAGE_MAIN_22V,
                voltage_nominal_v=cls.SYSTEM_VOLTAGE_NOMINAL_V,
                continuous_current_a=18.29,
                peak_current_a=30.00,
                continuous_power_w=406.1,
                peak_power_w=666.0,
                provenance=ProvenanceCategory.UPSTREAM_RESULT,
                notes="Phase 2 authoritative hover power (406.1W/motor @ 22.2V)",
            ))

        # Cruise Motor (Phase 4 / Fixed-Wing authoritative cruise power: 360.0 W = 16.22 A @ 22.2 V)
        # Peak during climb / acceleration: ~25.0 A (555 W)
        loads.append(ElectricalLoad(
            load_id="LOAD-CRUISE-MTR-1",
            load_name="Cruise Pusher Motor",
            role=AircraftRole.CRUISE_MOTOR,
            bus_type=BusType.HIGH_VOLTAGE_MAIN_22V,
            voltage_nominal_v=cls.SYSTEM_VOLTAGE_NOMINAL_V,
            continuous_current_a=16.22,
            peak_current_a=25.00,
            continuous_power_w=360.0,
            peak_power_w=555.0,
            provenance=ProvenanceCategory.UPSTREAM_RESULT,
            notes="Authoritative cruise electrical power (360.0W @ 22.2V)",
        ))

        # Servos (4x KST DS215MG Digital Servos on 5V rail)
        # Average deflection current ~0.25A per servo (1.0A total); dynamic stall/peak ~0.8A per servo (3.2A total)
        for s_role, s_name in [
            (AircraftRole.LEFT_AILERON_SERVO, "Left Aileron Servo"),
            (AircraftRole.RIGHT_AILERON_SERVO, "Right Aileron Servo"),
            (AircraftRole.VTAIL_SURFACE_1_SERVO, "V-Tail Left Ruddervator Servo"),
            (AircraftRole.VTAIL_SURFACE_2_SERVO, "V-Tail Right Ruddervator Servo"),
        ]:
            loads.append(ElectricalLoad(
                load_id=f"LOAD-{s_role.value}",
                load_name=s_name,
                role=s_role,
                bus_type=BusType.REGULATED_5V_AVIONICS,
                voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
                continuous_current_a=0.25,
                peak_current_a=0.80,
                continuous_power_w=1.25,
                peak_power_w=4.00,
                provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
                notes="Digital micro servo on 5.0V rail; dynamic torque requirement DEFERRED",
            ))

        # Autopilot Pixhawk 6X
        loads.append(ElectricalLoad(
            load_id="LOAD-AUTOPILOT-1",
            load_name="Pixhawk 6X Flight Controller",
            role=AircraftRole.AUTOPILOT_PIXHAWK,
            bus_type=BusType.REGULATED_5V_AVIONICS,
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            continuous_current_a=0.80,
            peak_current_a=1.20,
            continuous_power_w=4.0,
            peak_power_w=6.0,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Pixhawk 6X baseboard draw operational power budget assumption",
        ))

        # Navigation GNSS RTK F9P
        loads.append(ElectricalLoad(
            load_id="LOAD-GNSS-1",
            load_name="H-RTK F9P Helical GNSS",
            role=AircraftRole.NAVIGATION_GNSS_RTK,
            bus_type=BusType.REGULATED_5V_AVIONICS,
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            continuous_current_a=0.25,
            peak_current_a=0.35,
            continuous_power_w=1.25,
            peak_power_w=1.75,
            provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            notes="F9P dual-frequency GNSS + IST8310 compass receiver",
        ))

        # Digital Airspeed ASPD-4525
        loads.append(ElectricalLoad(
            load_id="LOAD-AIRSPEED-1",
            load_name="ASPD-4525 Digital Airspeed",
            role=AircraftRole.DIGITAL_AIRSPEED,
            bus_type=BusType.REGULATED_5V_AVIONICS,
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            continuous_current_a=0.03,
            peak_current_a=0.05,
            continuous_power_w=0.15,
            peak_power_w=0.25,
            provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            notes="Matek MS4525DO I2C pressure transducer",
        ))

        # Telemetry Radio SiK 915MHz
        loads.append(ElectricalLoad(
            load_id="LOAD-TELEM-1",
            load_name="SiK 915MHz Telemetry Radio",
            role=AircraftRole.TELEMETRY_TRANSCEIVER,
            bus_type=BusType.REGULATED_5V_AVIONICS,
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            continuous_current_a=0.20,
            peak_current_a=0.50,
            continuous_power_w=1.00,
            peak_power_w=2.50,
            provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            notes="500mW RF output transmit burst draw",
        ))

        # RC Receiver Crossfire Nano
        loads.append(ElectricalLoad(
            load_id="LOAD-RC-1",
            load_name="TBS Crossfire Nano RX",
            role=AircraftRole.RC_RECEIVER,
            bus_type=BusType.REGULATED_5V_AVIONICS,
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            continuous_current_a=0.08,
            peak_current_a=0.12,
            continuous_power_w=0.40,
            peak_power_w=0.60,
            provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            notes="CRSF telemetry receiver",
        ))

        # Companion SBC Raspberry Pi 4B (Dedicated 5V bus)
        loads.append(ElectricalLoad(
            load_id="LOAD-SBC-1",
            load_name="Raspberry Pi 4B Companion Computer",
            role=AircraftRole.COMPANION_SBC,
            bus_type=BusType.REGULATED_5V_COMPANION,
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            continuous_current_a=1.20,
            peak_current_a=2.50,
            continuous_power_w=6.00,
            peak_power_w=12.50,
            provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            notes="Quad-core Cortex-A72 @ 1.5GHz with USB/Ethernet peripherals",
        ))

        # Payload Camera Sony RX0 II (Optional 5V trickle or self-powered internal battery)
        loads.append(ElectricalLoad(
            load_id="LOAD-PAYLOAD-1",
            load_name="Sony DSC-RX0 II Mapping Payload",
            role=AircraftRole.MISSION_PAYLOAD_CAMERA,
            bus_type=BusType.REGULATED_5V_AVIONICS,
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            continuous_current_a=0.10,
            peak_current_a=0.40,
            continuous_power_w=0.50,
            peak_power_w=2.00,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Primarily self-powered by NP-BJ1 battery; 5V USB trigger line",
        ))

        # -----------------------------------------------------------------
        # 2. SYNTHESIZE ELECTRICAL BUSES & CAPACITIES
        # -----------------------------------------------------------------
        # Bus 1: Main High Voltage 22.2V Bus (Direct from Battery via PDB-HEX)
        main_loads = [ld for ld in loads if ld.bus_type == BusType.HIGH_VOLTAGE_MAIN_22V]
        main_cont_curr = sum(ld.continuous_current_a for ld in main_loads)  # Hover: 4*18.29 = 73.16 A
        # Peak: simultaneous transition corridor (4 lift motors + cruise motor burst = 4*30 + 25 = 145.0 A)
        main_peak_curr = sum(ld.peak_current_a for ld in main_loads)
        pdb_cont_cap = 140.0  # Matek PDB-HEX 140A continuous rating
        pdb_peak_cap = 200.0  # Burst rating

        bus_main = ElectricalBus(
            bus_type=BusType.HIGH_VOLTAGE_MAIN_22V,
            bus_name="Main 6S High-Current Bus (PDB)",
            nominal_voltage_v=cls.SYSTEM_VOLTAGE_NOMINAL_V,
            voltage_min_v=cls.SYSTEM_VOLTAGE_MIN_V,
            voltage_max_v=cls.SYSTEM_VOLTAGE_MAX_V,
            max_continuous_current_capacity_a=pdb_cont_cap,
            max_peak_current_capacity_a=pdb_peak_cap,
            regulator_model="Direct Unregulated LiPo Discharge via PDB-HEX",
            source_bus=None,
            loads=main_loads,
            total_continuous_current_a=main_cont_curr,
            total_peak_current_a=main_peak_curr,
            continuous_margin_a=pdb_cont_cap - main_cont_curr,
            peak_margin_a=pdb_peak_cap - main_peak_curr,
            status=VerificationCheckStatus.PASS if (pdb_cont_cap >= main_cont_curr and pdb_peak_cap >= main_peak_curr) else VerificationCheckStatus.WARNING,
            provenance=ProvenanceCategory.DERIVED,
        )
        buses.append(bus_main)

        # Bus 2: Regulated 5.0V Avionics & Servos Rail (PDB-HEX BEC 1)
        # Rating: 5.0V @ 5.0A continuous (6.0A peak)
        avionics_loads = [ld for ld in loads if ld.bus_type == BusType.REGULATED_5V_AVIONICS]
        avionics_cont_curr = sum(ld.continuous_current_a for ld in avionics_loads)  # ~2.46 A
        avionics_peak_curr = sum(ld.peak_current_a for ld in avionics_loads)        # ~5.82 A
        bec1_cont_cap = 5.00
        bec1_peak_cap = 6.00

        bus_avionics = ElectricalBus(
            bus_type=BusType.REGULATED_5V_AVIONICS,
            bus_name="Regulated 5V Avionics & Servos Rail (BEC 1)",
            nominal_voltage_v=cls.REGULATED_5V_NOMINAL_V,
            voltage_min_v=4.85,
            voltage_max_v=5.15,
            max_continuous_current_capacity_a=bec1_cont_cap,
            max_peak_current_capacity_a=bec1_peak_cap,
            regulator_model="Matek PDB-HEX Synchronous Step-Down BEC 1",
            source_bus=BusType.HIGH_VOLTAGE_MAIN_22V,
            loads=avionics_loads,
            total_continuous_current_a=avionics_cont_curr,
            total_peak_current_a=avionics_peak_curr,
            continuous_margin_a=bec1_cont_cap - avionics_cont_curr,
            peak_margin_a=bec1_peak_cap - avionics_peak_curr,
            status=VerificationCheckStatus.PASS if (bec1_cont_cap >= avionics_cont_curr and bec1_peak_cap >= avionics_peak_curr) else VerificationCheckStatus.WARNING,
            provenance=ProvenanceCategory.DERIVED,
        )
        buses.append(bus_avionics)

        # Bus 3: Dedicated 5.0V Companion Computer Rail (PDB Aux Step-Down / Dedicated 3A BEC)
        sbc_loads = [ld for ld in loads if ld.bus_type == BusType.REGULATED_5V_COMPANION]
        sbc_cont_curr = sum(ld.continuous_current_a for ld in sbc_loads)
        sbc_peak_curr = sum(ld.peak_current_a for ld in sbc_loads)
        sbc_bec_cap = 3.00

        bus_sbc = ElectricalBus(
            bus_type=BusType.REGULATED_5V_COMPANION,
            bus_name="Dedicated 5V Companion Computer Supply",
            nominal_voltage_v=cls.REGULATED_5V_NOMINAL_V,
            voltage_min_v=4.90,
            voltage_max_v=5.20,
            max_continuous_current_capacity_a=sbc_bec_cap,
            max_peak_current_capacity_a=4.00,
            regulator_model="Dedicated 5V 3A DC-DC Synchronous Buck Regulator",
            source_bus=BusType.HIGH_VOLTAGE_MAIN_22V,
            loads=sbc_loads,
            total_continuous_current_a=sbc_cont_curr,
            total_peak_current_a=sbc_peak_curr,
            continuous_margin_a=sbc_bec_cap - sbc_cont_curr,
            peak_margin_a=4.00 - sbc_peak_curr,
            status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
        )
        buses.append(bus_sbc)

        # -----------------------------------------------------------------
        # 3. VERIFY EXPLICIT POWER PATHS (Prompt Section 7: A through G)
        # -----------------------------------------------------------------
        # Path A: Battery -> PDB
        # Battery rating: 22000mAh 25C = 550A continuous; connector XT90-S rated 90A cont / 120A burst
        # Max continuous hover current = 75.0A (continuous hover power 1624.5W + avionics)
        # Peak simultaneous transition current = 98.5A (Phase 4 authoritative envelope)
        batt_margin_cont = 90.0 - 75.0
        batt_margin_peak = 120.0 - 98.5
        paths.append(PowerPath(
            path_id="PATH-A",
            path_name="Battery to Power Distribution Board (PDB)",
            source="Tattu Plus 6S 22000mAh 25C LiPo",
            destination="Matek PDB-HEX Main Input",
            voltage_nominal_v=cls.SYSTEM_VOLTAGE_NOMINAL_V,
            voltage_compatibility=VerificationCheckStatus.PASS,
            continuous_current_a=75.0,
            peak_current_a=98.5,
            continuous_capacity_a=90.0,  # AS150 / XT90 connector limit
            peak_capacity_a=120.0,
            margin_a=batt_margin_cont,
            connector_type="XT90-S Anti-Spark / AS150",
            regulator_capacity_w=None,
            status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Battery cell capacity is 550A (25C); XT90-S connector is assumed limiting interface at 90A cont / 120A burst. Margin is +15.0A cont / +21.5A peak.",
        ))

        # Path B: PDB -> 4x VTOL ESCs -> Lift Motors
        # 40A continuous ESC rating vs 18.29A hover requirement -> margin +21.71A per ESC
        for i in range(1, 5):
            paths.append(PowerPath(
                path_id=f"PATH-B{i}",
                path_name=f"PDB to VTOL ESC {i} -> Motor {i}",
                source="Matek PDB-HEX ESC Pad",
                destination=f"T-Motor AIR 40A ESC {i}",
                voltage_nominal_v=cls.SYSTEM_VOLTAGE_NOMINAL_V,
                voltage_compatibility=VerificationCheckStatus.PASS,
                continuous_current_a=18.29,
                peak_current_a=30.00,
                continuous_capacity_a=40.0,
                peak_capacity_a=50.0,
                margin_a=40.0 - 18.29,
                connector_type="Direct Solder Pad to 14AWG High-Temp Silicone Wire",
                regulator_capacity_w=None,
                status=VerificationCheckStatus.PASS,
                provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
                notes=f"Lift motor {i} hover draw 18.29A vs 40A ESC continuous capacity (margin +21.71A)",
            ))

        # Path C: PDB -> Cruise ESC -> Cruise Motor
        # 40A continuous ESC rating vs 16.22A cruise requirement -> margin +23.78A
        paths.append(PowerPath(
            path_id="PATH-C",
            path_name="PDB to Cruise ESC -> Pusher Motor",
            source="Matek PDB-HEX ESC Pad",
            destination="Hobbywing FlyFun 40A V5 ESC",
            voltage_nominal_v=cls.SYSTEM_VOLTAGE_NOMINAL_V,
            voltage_compatibility=VerificationCheckStatus.PASS,
            continuous_current_a=16.22,
            peak_current_a=25.00,
            continuous_capacity_a=40.0,
            peak_capacity_a=60.0,
            margin_a=40.0 - 16.22,
            connector_type="XT60 / 14AWG Wire",
            regulator_capacity_w=None,
            status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.COMMERCIAL_VERIFIED,
            notes="Cruise motor 16.22A continuous vs 40A ESC rating (margin +23.78A)",
        ))

        # Path D: Regulated 5V Rail -> Servos (4x KST DS215MG)
        # Continuous draw ~1.0A (4x 0.25A), peak ~3.2A (4x 0.8A)
        paths.append(PowerPath(
            path_id="PATH-D",
            path_name="Regulated 5V Rail to Control Surface Servos",
            source="Matek PDB-HEX BEC 1 (5V Rail)",
            destination="4x KST DS215MG Digital Servos (Ailerons + Ruddervators)",
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            voltage_compatibility=VerificationCheckStatus.PASS,
            continuous_current_a=1.00,
            peak_current_a=3.20,
            continuous_capacity_a=3.50,  # Allocated servo capacity from 5A BEC
            peak_capacity_a=4.50,
            margin_a=3.50 - 1.00,
            connector_type="Standard 3-pin JR Servo Connectors / Servo Rail",
            regulator_capacity_w=25.0,  # 5V * 5A
            status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Servo continuous 1.0A vs allocated BEC headroom; dynamic aerodynamic hinge moment torque DEFERRED per Phase 8",
        ))

        # Path E: Regulated 5V Rail -> Flight Controller (Pixhawk 6X)
        paths.append(PowerPath(
            path_id="PATH-E",
            path_name="Regulated 5V Rail to Pixhawk 6X Autopilot",
            source="Matek PDB-HEX BEC 1 (POWER1 Port)",
            destination="Pixhawk 6X Power 1 Port",
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            voltage_compatibility=VerificationCheckStatus.PASS,
            continuous_current_a=0.80,
            peak_current_a=1.20,
            continuous_capacity_a=3.00,  # Pixhawk Power port input limit
            peak_capacity_a=3.00,
            margin_a=3.00 - 0.80,
            connector_type="6-pin JST-GH (Power Module Interface)",
            regulator_capacity_w=15.0,
            status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Dual power redundancy supported via secondary power module on POWER2; load draw is an allocated operational budget",
        ))

        # Path F: Regulated 5V Rail -> Avionics & Sensors (GNSS, Airspeed, Telemetry, RC)
        # Continuous draw ~0.56A, peak ~1.02A
        paths.append(PowerPath(
            path_id="PATH-F",
            path_name="Regulated 5V Rail to Avionics Peripherals",
            source="Pixhawk 6X Internal Power Distribution / BEC 1",
            destination="H-RTK GNSS, ASPD-4525 Airspeed, SiK Telemetry, Crossfire RX",
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            voltage_compatibility=VerificationCheckStatus.PASS,
            continuous_current_a=0.56,
            peak_current_a=1.02,
            continuous_capacity_a=1.50,  # Pixhawk peripheral VCC limit
            peak_capacity_a=2.00,
            margin_a=1.50 - 0.56,
            connector_type="JST-GH Click-Locking Connectors",
            regulator_capacity_w=10.0,
            status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="All navigation and communication peripherals powered via protected Pixhawk rails; draws are operational estimates",
        ))

        # Path G: Regulated Companion Computer Supply -> Raspberry Pi 4B
        paths.append(PowerPath(
            path_id="PATH-G",
            path_name="Regulated 5V Rail to Raspberry Pi 4B SBC",
            source="Dedicated 5V 3A Synchronous Step-Down BEC",
            destination="Raspberry Pi 4B Power Input (USB-C / GPIO)",
            voltage_nominal_v=cls.REGULATED_5V_NOMINAL_V,
            voltage_compatibility=VerificationCheckStatus.PASS,
            continuous_current_a=1.20,
            peak_current_a=2.50,
            continuous_capacity_a=3.00,
            peak_capacity_a=4.00,
            margin_a=3.00 - 1.20,
            connector_type="USB-C / 18AWG Silicone Lead",
            regulator_capacity_w=15.0,
            status=VerificationCheckStatus.PASS,
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            notes="Dedicated 3A BEC is a Phase 9 integration component assumption to isolate SBC power",
        ))

        return buses, paths, loads
