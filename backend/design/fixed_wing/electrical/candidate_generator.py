"""
Electrical System Candidate Generator

Defines the electrical components catalog and the candidate generator.
"""

from typing import List, Dict, Any
from backend.design.components.component_category import ComponentCategory
from backend.design.components.component_repository import ComponentRepository
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


def build_electrical_repository() -> ComponentRepository:
    """Builds and populates the component database for electrical system design."""
    repo = ComponentRepository()

    # 1. Flight Controllers
    repo.register_component(ComponentCategory.FLIGHT_CONTROLLER, {
        "name": "Matek H743-WING", "weight_g": 30.0, "triple_redundant": False, "price": 120.0,
        "interfaces": ["PWM", "UART", "CAN"], "current_draw_a": 0.15, "voltage_v": 5.0
    })
    repo.register_component(ComponentCategory.FLIGHT_CONTROLLER, {
        "name": "Holybro Pixhawk 6C", "weight_g": 45.0, "triple_redundant": False, "price": 220.0,
        "interfaces": ["PWM", "UART", "CAN", "Ethernet"], "current_draw_a": 0.25, "voltage_v": 5.0
    })
    repo.register_component(ComponentCategory.FLIGHT_CONTROLLER, {
        "name": "Cube Orange+", "weight_g": 75.0, "triple_redundant": True, "price": 450.0,
        "interfaces": ["PWM", "UART", "CAN", "Ethernet", "SPI"], "current_draw_a": 0.35, "voltage_v": 5.0
    })
    repo.register_component(ComponentCategory.FLIGHT_CONTROLLER, {
        "name": "Holybro Pixhawk 6X", "weight_g": 80.0, "triple_redundant": True, "price": 490.0,
        "interfaces": ["PWM", "UART", "CAN", "Ethernet", "SPI"], "current_draw_a": 0.40, "voltage_v": 5.0
    })

    # 2. GPS Modules
    repo.register_component(ComponentCategory.GPS, {
        "name": "Holybro Micro M8N", "weight_g": 15.0, "supports_rtk": False, "supports_dual": False,
        "price": 35.0, "current_draw_a": 0.05, "voltage_v": 5.0
    })
    repo.register_component(ComponentCategory.GPS, {
        "name": "Holybro M9N GNSS", "weight_g": 22.0, "supports_rtk": False, "supports_dual": True,
        "price": 65.0, "current_draw_a": 0.08, "voltage_v": 5.0
    })
    repo.register_component(ComponentCategory.GPS, {
        "name": "CubePilot Here3 RTK", "weight_g": 48.0, "supports_rtk": True, "supports_dual": True,
        "price": 250.0, "current_draw_a": 0.12, "voltage_v": 5.0
    })
    repo.register_component(ComponentCategory.GPS, {
        "name": "CubePilot Here4 RTK", "weight_g": 52.0, "supports_rtk": True, "supports_dual": True,
        "price": 320.0, "current_draw_a": 0.15, "voltage_v": 5.0
    })

    # 3. Telemetry Radios
    repo.register_component(ComponentCategory.TELEMETRY, {
        "name": "Holybro SiK 915MHz Radio", "weight_g": 16.0, "max_range_km": 5.0, "max_bandwidth_kbps": 64.0,
        "power_w": 0.5, "voltage_v": 5.0, "frequency_mhz": 915.0, "price": 40.0
    })
    repo.register_component(ComponentCategory.TELEMETRY, {
        "name": "RFDesign RFD900ux", "weight_g": 28.0, "max_range_km": 40.0, "max_bandwidth_kbps": 224.0,
        "power_w": 1.0, "voltage_v": 5.0, "frequency_mhz": 915.0, "price": 110.0
    })
    repo.register_component(ComponentCategory.TELEMETRY, {
        "name": "Microhard PMDDL2450", "weight_g": 45.0, "max_range_km": 50.0, "max_bandwidth_kbps": 3100.0,
        "power_w": 2.5, "voltage_v": 12.0, "frequency_mhz": 2400.0, "price": 280.0
    })
    repo.register_component(ComponentCategory.TELEMETRY, {
        "name": "Silvus StreamCaster Lite", "weight_g": 110.0, "max_range_km": 80.0, "max_bandwidth_kbps": 15000.0,
        "power_w": 6.0, "voltage_v": 12.0, "frequency_mhz": 2400.0, "price": 950.0
    })

    # 4. RC Receivers
    repo.register_component(ComponentCategory.RECEIVER, {
        "name": "FrSky Archer RS", "weight_g": 3.0, "protocol": "SBUS", "typical_range_km": 2.0,
        "frequency_mhz": 2400.0, "current_draw_a": 0.03, "voltage_v": 5.0, "price": 25.0
    })
    repo.register_component(ComponentCategory.RECEIVER, {
        "name": "ExpressLRS 2.4G RX", "weight_g": 5.0, "protocol": "CRSF", "typical_range_km": 8.0,
        "frequency_mhz": 2400.0, "current_draw_a": 0.05, "voltage_v": 5.0, "price": 30.0
    })
    repo.register_component(ComponentCategory.RECEIVER, {
        "name": "ExpressLRS 915M RX", "weight_g": 7.0, "protocol": "CRSF", "typical_range_km": 25.0,
        "frequency_mhz": 915.0, "current_draw_a": 0.06, "voltage_v": 5.0, "price": 35.0
    })
    repo.register_component(ComponentCategory.RECEIVER, {
        "name": "TBS Crossfire Nano RX", "weight_g": 8.0, "protocol": "CRSF", "typical_range_km": 40.0,
        "frequency_mhz": 915.0, "current_draw_a": 0.08, "voltage_v": 5.0, "price": 45.0
    })

    # 5. Servos
    repo.register_component(ComponentCategory.SERVO, {
        "name": "KST X08 Micro Servo", "weight_g": 8.0, "torque_kgcm": 1.4, "voltage_v": 5.0,
        "peak_current_a": 0.8, "continuous_current_a": 0.25, "price": 38.0
    })
    repo.register_component(ComponentCategory.SERVO, {
        "name": "KST DS125MG Wing Servo", "weight_g": 28.0, "torque_kgcm": 5.5, "voltage_v": 6.0,
        "peak_current_a": 1.5, "continuous_current_a": 0.45, "price": 55.0
    })
    repo.register_component(ComponentCategory.SERVO, {
        "name": "KST X20 High-Torque Servo", "weight_g": 72.0, "torque_kgcm": 16.0, "voltage_v": 7.4,
        "peak_current_a": 2.6, "continuous_current_a": 0.75, "price": 120.0
    })

    # 6. BECs (Voltage Regulators for Servo Rails)
    repo.register_component(ComponentCategory.BEC, {
        "name": "KDE Direct 3A BEC", "weight_g": 9.0, "voltage_v": 5.0, "max_continuous_current_a": 3.0,
        "max_peak_current_a": 5.0, "price": 20.0
    })
    repo.register_component(ComponentCategory.BEC, {
        "name": "Matek 6A BEC", "weight_g": 14.0, "voltage_v": 6.0, "max_continuous_current_a": 6.0,
        "max_peak_current_a": 10.0, "price": 25.0
    })
    repo.register_component(ComponentCategory.BEC, {
        "name": "Castle Creations 10A BEC", "weight_g": 18.0, "voltage_v": 6.0, "max_continuous_current_a": 10.0,
        "max_peak_current_a": 15.0, "price": 35.0
    })
    repo.register_component(ComponentCategory.BEC, {
        "name": "Castle Pro 20A BEC", "weight_g": 29.0, "voltage_v": 7.4, "max_continuous_current_a": 20.0,
        "max_peak_current_a": 30.0, "price": 55.0
    })

    # 7. Power Modules / Current Sensors
    repo.register_component(ComponentCategory.POWER_DISTRIBUTION_BOARD, {
        "name": "Holybro PM02 30A Module", "weight_g": 14.0, "max_voltage_cells_s": 6, "max_continuous_current_a": 30.0,
        "price": 20.0
    })
    repo.register_component(ComponentCategory.POWER_DISTRIBUTION_BOARD, {
        "name": "Holybro PM06 100A Module", "weight_g": 24.0, "max_voltage_cells_s": 12, "max_continuous_current_a": 100.0,
        "price": 38.0
    })
    repo.register_component(ComponentCategory.POWER_DISTRIBUTION_BOARD, {
        "name": "Maucher Hall 200A Module", "weight_g": 40.0, "max_voltage_cells_s": 14, "max_continuous_current_a": 200.0,
        "price": 85.0
    })

    # 8. Connectors
    repo.register_component(ComponentCategory.CUSTOM, {
        "name": "XT30 Connector", "category": "Connector", "weight_g": 2.0, "max_continuous_current_a": 30.0, "price": 1.0
    })
    repo.register_component(ComponentCategory.CUSTOM, {
        "name": "XT60 Connector", "category": "Connector", "weight_g": 4.0, "max_continuous_current_a": 60.0, "price": 2.0
    })
    repo.register_component(ComponentCategory.CUSTOM, {
        "name": "XT90 Connector", "category": "Connector", "weight_g": 8.0, "max_continuous_current_a": 90.0, "price": 3.0
    })
    repo.register_component(ComponentCategory.CUSTOM, {
        "name": "AS150 Connector", "category": "Connector", "weight_g": 14.0, "max_continuous_current_a": 150.0, "price": 6.0
    })

    # 9. Mission Equipment / Payloads
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "GoPro Hero 11 FPV Camera", "category": "Mapping Camera", "weight_g": 154.0, "power_w": 4.0,
        "interfaces": ["UART"], "price": 399.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "FLIR Duo Pro R Thermal Camera", "category": "Thermal Camera", "weight_g": 220.0, "power_w": 8.0,
        "interfaces": ["UART", "CAN"], "price": 4800.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "MicaSense Altum Multispectral Camera", "category": "Multispectral Camera", "weight_g": 350.0, "power_w": 12.0,
        "interfaces": ["UART", "CAN", "Ethernet"], "price": 5400.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "Sony RX1R II Survey Camera", "category": "Mapping Camera", "weight_g": 507.0, "power_w": 6.0,
        "interfaces": ["UART"], "price": 3299.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "Benewake TFmini Plus Lidar", "category": "LiDAR", "weight_g": 12.0, "power_w": 0.5,
        "interfaces": ["UART", "I2C"], "price": 45.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "YellowScan Mapper LiDAR", "category": "LiDAR", "weight_g": 1200.0, "power_w": 15.0,
        "interfaces": ["UART", "Ethernet"], "price": 24000.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "Heavy Sprayer Valve & Servo", "category": "Agriculture Sprayer", "weight_g": 280.0, "power_w": 20.0,
        "interfaces": ["PWM"], "price": 180.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "Cargo Box Release Servo", "category": "Cargo Drop Box", "weight_g": 45.0, "power_w": 2.0,
        "interfaces": ["PWM"], "price": 30.0
    })
    repo.register_component(ComponentCategory.PAYLOAD, {
        "name": "Custom Instrument Payload Interface", "category": "Custom Payload Interface", "weight_g": 85.0, "power_w": 5.0,
        "interfaces": ["CAN", "UART"], "price": 75.0
    })

    # 10. Sensors
    repo.register_component(ComponentCategory.SENSOR, {
        "name": "MS5611 Barometer", "weight_g": 2.0, "category": "Barometer", "interface": "I2C", "power_w": 0.01
    })
    repo.register_component(ComponentCategory.SENSOR, {
        "name": "Holybro Digital Airspeed Sensor", "weight_g": 10.0, "category": "Airspeed", "interface": "I2C", "power_w": 0.1
    })
    repo.register_component(ComponentCategory.SENSOR, {
        "name": "Matek CAN Compass", "weight_g": 8.0, "category": "Compass", "interface": "CAN", "power_w": 0.15
    })

    # 11. Wire AWGs
    wire_db = [
        {"name": "10 AWG Wire", "awg": 10, "max_continuous_current_a": 140.0, "resistance_mohm_per_m": 3.27, "weight_g_per_m": 38.0},
        {"name": "12 AWG Wire", "awg": 12, "max_continuous_current_a": 90.0, "resistance_mohm_per_m": 5.21, "weight_g_per_m": 24.0},
        {"name": "14 AWG Wire", "awg": 14, "max_continuous_current_a": 60.0, "resistance_mohm_per_m": 8.28, "weight_g_per_m": 15.0},
        {"name": "16 AWG Wire", "awg": 16, "max_continuous_current_a": 35.0, "resistance_mohm_per_m": 13.17, "weight_g_per_m": 9.5},
        {"name": "18 AWG Wire", "awg": 18, "max_continuous_current_a": 20.0, "resistance_mohm_per_m": 20.95, "weight_g_per_m": 6.0},
        {"name": "20 AWG Wire", "awg": 20, "max_continuous_current_a": 11.0, "resistance_mohm_per_m": 33.31, "weight_g_per_m": 3.8},
        {"name": "22 AWG Wire", "awg": 22, "max_continuous_current_a": 7.0, "resistance_mohm_per_m": 52.96, "weight_g_per_m": 2.4},
    ]
    for w in wire_db:
        repo.register_component(ComponentCategory.CUSTOM, {
            "name": w["name"], "category": "Wire", "awg": w["awg"],
            "max_continuous_current_a": w["max_continuous_current_a"],
            "resistance_mohm_per_m": w["resistance_mohm_per_m"],
            "weight_g_per_m": w["weight_g_per_m"], "price": w["awg"] * 0.1
        })

    return repo


class ElectricalCandidateGenerator:
    """Generates feasible and logically pruned electrical candidates."""

    def __init__(self, repository: ComponentRepository | None = None) -> None:
        self.repository = repository if repository else build_electrical_repository()

    def generate_candidates(self, context: OptimizationContext) -> List[OptimizationCandidate]:
        """Generates pruned electrical layout design combinations."""
        # 1. Retrieve catalogs
        fcs = self.repository.get_components_by_category(ComponentCategory.FLIGHT_CONTROLLER)
        gps_units = self.repository.get_components_by_category(ComponentCategory.GPS)
        telemetries = self.repository.get_components_by_category(ComponentCategory.TELEMETRY)
        receivers = self.repository.get_components_by_category(ComponentCategory.RECEIVER)
        servos = self.repository.get_components_by_category(ComponentCategory.SERVO)
        becs = self.repository.get_components_by_category(ComponentCategory.BEC)
        pms = self.repository.get_components_by_category(ComponentCategory.POWER_DISTRIBUTION_BOARD)
        connectors = [c for c in self.repository.get_components_by_category(ComponentCategory.CUSTOM) if c["category"] == "Connector"]
        payloads = self.repository.get_components_by_category(ComponentCategory.PAYLOAD)
        wires = [w for w in self.repository.get_components_by_category(ComponentCategory.CUSTOM) if w["category"] == "Wire"]

        # Context metrics
        profile = context.requirements.mission_result.mission_profile
        category = profile.mission_category.value if hasattr(profile.mission_category, "value") else str(profile.mission_category)
        range_target_km = profile.mission_range_km
        mtow = (
            getattr(profile, "maximum_takeoff_weight_limit_kg", None)
            or getattr(profile, "current_iteration_mtow_kg", None)
            or getattr(profile, "initial_mtow_seed_kg", None)
            or 10.0
        )
        v_cruise = profile.cruise_speed_kmh

        # Extract propulsion spec cells count to ensure compatibility
        prop_spec = context.previous_specifications.get("PropulsionOptimizer")
        prop_cells = 6  # fallback default
        if prop_spec:
            # We look at the battery cell count
            prop_cells = getattr(prop_spec, "battery_cell_count", 6)
            # Check if there is motor_cell_count
            if hasattr(prop_spec, "operating_voltage_v"):
                v = getattr(prop_spec, "operating_voltage_v")
                if v > 40.0:
                    prop_cells = 12
                elif v > 20.0:
                    prop_cells = 6
                else:
                    prop_cells = 3

        # Match payloads based on mission category
        matched_payload = None
        for p in payloads:
            p_cat = p["category"]
            if category.lower() == "survey" and "Thermal" in p_cat:
                matched_payload = p
                break
            elif category.lower() == "mapping" and "Sony RX1R" in p["name"]:
                matched_payload = p
                break
            elif category.lower() == "agriculture" and "Sprayer" in p_cat:
                matched_payload = p
                break
            elif category.lower() == "cargo" and "Cargo Box" in p_cat:
                matched_payload = p
                break
            elif category.lower() == "research" and "Custom Instrument" in p_cat:
                matched_payload = p
                break
        if not matched_payload:
            # fallback payload
            matched_payload = payloads[0]

        # Settle redundancy levels: BVLOS/Cargo need redundant avionics and dual power buses
        needs_redundancy = "cargo" in category.lower() or range_target_km > 20.0

        # Filter Flight Controllers
        valid_fcs = []
        for fc in fcs:
            if needs_redundancy and not fc["triple_redundant"]:
                continue
            if not needs_redundancy and fc["triple_redundant"]:
                continue
            # If payload needs Ethernet, FC must have Ethernet
            if "Ethernet" in matched_payload.get("interfaces", []) and "Ethernet" not in fc["interfaces"]:
                continue
            valid_fcs.append(fc)
        if not valid_fcs:
            valid_fcs = [fcs[-1]]  # fallback 6X

        # Filter GPS
        valid_gps = []
        needs_rtk = category.lower() in ("survey", "mapping")
        for g in gps_units:
            if needs_rtk and not g["supports_rtk"]:
                continue
            if not needs_rtk and g["supports_rtk"]:
                continue
            valid_gps.append(g)
        if not valid_gps:
            valid_gps = [gps_units[-1]]

        # Filter Telemetry
        valid_telemetries = []
        for t in telemetries:
            if t["max_range_km"] >= range_target_km:
                # BVLOS/Video payloads need high bandwidth (Microhard or Silvus)
                if range_target_km > 30.0 and t["max_bandwidth_kbps"] < 1000.0:
                    continue
                valid_telemetries.append(t)
        if not valid_telemetries:
            valid_telemetries = [telemetries[-1]]
        # Pick the lightest/cheapest telemetry that passes range
        best_telem = min(valid_telemetries, key=lambda t: t["price"])

        # Filter Receivers
        valid_receivers = []
        for r in receivers:
            if r["typical_range_km"] >= range_target_km:
                # Keep frequency band compatible if possible
                valid_receivers.append(r)
        if not valid_receivers:
            valid_receivers = [receivers[-1]]
        best_rx = min(valid_receivers, key=lambda r: r["weight_g"])

        # Select Servos based on required torque
        required_servo_torque_kgcm = mtow * (v_cruise / 50.0) * 0.5
        best_servo = None
        for s in servos:
            if s["torque_kgcm"] >= required_servo_torque_kgcm:
                best_servo = s
                break
        if not best_servo:
            best_servo = servos[-1]

        # Determine Servo Count: default 4 (Ailerons, Elevator, Rudder)
        servo_count = 4
        tail_spec = context.previous_specifications.get("TailOptimizer")
        if tail_spec:
            cfg = getattr(tail_spec, "tail_configuration", "Conventional")
            if cfg == "V-Tail" or cfg == "Inverted V-Tail":
                servo_count = 4
            elif cfg == "Twin Boom":
                servo_count = 4

        # Select BEC matching servo voltage rating
        valid_becs = []
        for b in becs:
            if b["voltage_v"] == best_servo["voltage_v"]:
                valid_becs.append(b)
        if not valid_becs:
            valid_becs = [becs[1]]
        best_bec = min(valid_becs, key=lambda b: b["price"])

        # Select Power Module based on cells S
        valid_pms = []
        for pm in pms:
            if pm["max_voltage_cells_s"] >= prop_cells:
                valid_pms.append(pm)
        if not valid_pms:
            valid_pms = [pms[-1]]
        best_pm = min(valid_pms, key=lambda pm: pm["price"])

        # Generate layout candidates
        layouts = ["Single Bus"]
        if needs_redundancy:
            layouts.append("Dual Redundant Bus")

        candidates = []
        for fc in valid_fcs:
            for gps in valid_gps:
                for lay in layouts:
                    # Let evaluate_candidate size wires and connectors based on actual currents
                    # But we provide placeholders to be populated
                    design_vars = {
                        "flight_controller": fc,
                        "flight_controller_name": fc["name"],
                        "gps": gps,
                        "gps_name": gps["name"],
                        "telemetry": best_telem,
                        "telemetry_name": best_telem["name"],
                        "receiver": best_rx,
                        "receiver_name": best_rx["name"],
                        "servo": best_servo,
                        "servo_name": best_servo["name"],
                        "servo_count": servo_count,
                        "bec": best_bec,
                        "bec_name": best_bec["name"],
                        "power_module": best_pm,
                        "power_module_name": best_pm["name"],
                        "mission_equipment": matched_payload,
                        "mission_equipment_name": matched_payload["name"],
                        "power_distribution_layout": lay,
                    }
                    candidates.append(OptimizationCandidate(
                        design_variables=design_vars,
                        derived_variables={},
                        status="PENDING"
                    ))

        return candidates
