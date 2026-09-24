"""
Fixed-Wing Structural Component Database Subsystem

Purpose:
    Defines structural and mechanism hardware items (servos, linkages, pushrods,
    horns, motor mounts, battery/equipment trays, wheels, landing gear blocks) with
    realistic physical masses and properties.

Role in Architecture:
    Enables itemized structural component mass accounting without hiding mechanism
    hardware under arbitrary lumped coefficients.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(slots=True)
class ServoComponent:
    component_id: str
    name: str
    size_class: str  # "micro_9g", "mini_17g", "standard_45g"
    mass_kg: float
    torque_kg_cm: float
    voltage_v: float = 5.0
    cost_usd: float = 15.0
    notes: str = ""


@dataclass(slots=True)
class LinkageHardware:
    component_id: str
    name: str
    category: str  # "pushrod", "control_horn", "clevis", "ball_link"
    mass_per_unit_kg: float
    notes: str = ""


@dataclass(slots=True)
class WheelComponent:
    component_id: str
    name: str
    diameter_mm: float
    width_mm: float
    mass_kg: float
    cost_usd: float = 8.0
    notes: str = ""


@dataclass(slots=True)
class StructuralMountItem:
    component_id: str
    name: str
    category: str  # "motor_mount", "firewall", "battery_tray", "payload_tray", "gear_mount"
    typical_mass_kg: float
    material: str
    notes: str = ""


class StructuralComponentDatabase:
    """
    Standard catalog of structural mechanism components.
    """

    SERVOS: Dict[str, ServoComponent] = {
        "SERVO_9G_MICRO": ServoComponent(
            component_id="SERVO_9G_MICRO",
            name="Micro Metal Gear 9g Servo (e.g. EMAX ES08MDII)",
            size_class="micro_9g",
            mass_kg=0.012,  # 12g with lead and horn
            torque_kg_cm=2.4,
            notes="Ailerons, elevator, rudder on small UAVs (< 3.0 kg MTOW)."
        ),
        "SERVO_17G_MINI": ServoComponent(
            component_id="SERVO_17G_MINI",
            name="Mini Metal Gear 17g Servo (e.g. KST DS215MG / Corona CS238MG)",
            size_class="mini_17g",
            mass_kg=0.022,  # 22g with lead and hardware
            torque_kg_cm=4.6,
            notes="Primary flight control surfaces for 3.0 to 10.0 kg MTOW fixed-wing aircraft."
        ),
        "SERVO_45G_STANDARD": ServoComponent(
            component_id="SERVO_45G_STANDARD",
            name="Standard Coreless High-Torque 45g Servo",
            size_class="standard_45g",
            mass_kg=0.055,  # 55g with heavy arm and lead
            torque_kg_cm=14.0,
            notes="Flaps, high-speed ailerons, or nose steering on heavy UAVs (> 10.0 kg MTOW)."
        ),
    }

    LINKAGES: Dict[str, LinkageHardware] = {
        "PUSHROD_CARBON_STEEL": LinkageHardware(
            component_id="PUSHROD_CARBON_STEEL",
            name="Carbon Sleeve Pushrod with Threaded Steel Coupler (200mm)",
            category="pushrod",
            mass_per_unit_kg=0.008,
            notes="Zero-backlash control surface pushrod."
        ),
        "CONTROL_HORN_FIBER": LinkageHardware(
            component_id="CONTROL_HORN_FIBER",
            name="Glass-Filled Nylon / G10 Control Horn",
            category="control_horn",
            mass_per_unit_kg=0.003,
            notes="Surface mounting control horn."
        ),
        "CLEVIS_BALL_LINK": LinkageHardware(
            component_id="CLEVIS_BALL_LINK",
            name="M2 Steel Clevis & Brass Ball Link Assembly",
            category="clevis",
            mass_per_unit_kg=0.003,
            notes="Precision linkage end."
        ),
    }

    WHEELS: Dict[str, WheelComponent] = {
        "WHEEL_LIGHT_50MM": WheelComponent(
            component_id="WHEEL_LIGHT_50MM",
            name="Ultralight EVA Foam Wheel 50mm (2.0 in)",
            diameter_mm=50.0,
            width_mm=16.0,
            mass_kg=0.008,
            notes="Lightweight runway wheel for 1.5 - 4.0 kg UAVs."
        ),
        "WHEEL_STANDARD_65MM": WheelComponent(
            component_id="WHEEL_STANDARD_65MM",
            name="PU Tread Alloy Hub Wheel 65mm (2.5 in)",
            diameter_mm=65.0,
            width_mm=22.0,
            mass_kg=0.028,
            notes="Paved / smooth grass runway wheel for 4.0 - 10.0 kg UAVs."
        ),
        "WHEEL_ROUGH_85MM": WheelComponent(
            component_id="WHEEL_ROUGH_85MM",
            name="Semi-Pneumatic Tundra Wheel 85mm (3.3 in)",
            diameter_mm=85.0,
            width_mm=28.0,
            mass_kg=0.055,
            notes="Unprepared rural grass runway wheel for 6.0 - 15.0 kg UAVs."
        ),
    }

    MOUNTS_AND_TRAYS: Dict[str, StructuralMountItem] = {
        "FIREWALL_PLYWOOD": StructuralMountItem(
            component_id="FIREWALL_PLYWOOD",
            name="CNC Aircraft Birch Plywood Firewall (4mm)",
            category="firewall",
            typical_mass_kg=0.045,
            material="Birch Plywood",
            notes="Front motor mount structural bulkhead with blind nuts."
        ),
        "MOTOR_MOUNT_ALU_X": StructuralMountItem(
            component_id="MOTOR_MOUNT_ALU_X",
            name="CNC 6061 Aluminum Motor X-Mount Plate",
            category="motor_mount",
            typical_mass_kg=0.022,
            material="Aluminum 6061-T6",
            notes="Cross mount plate connecting brushless motor to firewall."
        ),
        "BATTERY_TRAY_CARBON": StructuralMountItem(
            component_id="BATTERY_TRAY_CARBON",
            name="Carbon Composite Battery Mounting Sled & Straps",
            category="battery_tray",
            typical_mass_kg=0.035,
            material="Carbon Fiber / Plywood",
            notes="Quick-release sliding tray with Hook-and-Loop straps."
        ),
        "PAYLOAD_TRAY_ISOLATED": StructuralMountItem(
            component_id="PAYLOAD_TRAY_ISOLATED",
            name="Vibration-Isolated Payload Bay Equipment Shelf",
            category="payload_tray",
            typical_mass_kg=0.040,
            material="Carbon / Silicone Dampers",
            notes="Gimbal / survey sensor mounting plate."
        ),
        "GEAR_MOUNT_HARDPOINT": StructuralMountItem(
            component_id="GEAR_MOUNT_HARDPOINT",
            name="Plywood / Glass Reinforced Landing Gear Mount Block",
            category="gear_mount",
            typical_mass_kg=0.050,
            material="Aircraft Plywood / Glass",
            notes="Distributes runway touchdown impact forces to fuselage longerons."
        ),
    }

    @classmethod
    def get_servo(cls, component_id: str) -> ServoComponent:
        if component_id not in cls.SERVOS:
            raise KeyError(f"Servo '{component_id}' not found in StructuralComponentDatabase.")
        return cls.SERVOS[component_id]

    @classmethod
    def get_servo_for_class(cls, size_class: str) -> ServoComponent:
        for servo in cls.SERVOS.values():
            if servo.size_class == size_class:
                return servo
        raise KeyError(f"Servo class '{size_class}' not found in StructuralComponentDatabase.")

    @classmethod
    def get_linkage(cls, component_id: str) -> LinkageHardware:
        if component_id not in cls.LINKAGES:
            raise KeyError(f"Linkage '{component_id}' not found in StructuralComponentDatabase.")
        return cls.LINKAGES[component_id]

    @classmethod
    def get_wheel(cls, component_id: str) -> WheelComponent:
        if component_id not in cls.WHEELS:
            raise KeyError(f"Wheel '{component_id}' not found in StructuralComponentDatabase.")
        return cls.WHEELS[component_id]

    @classmethod
    def get_mount(cls, component_id: str) -> StructuralMountItem:
        if component_id not in cls.MOUNTS_AND_TRAYS:
            raise KeyError(f"Mount item '{component_id}' not found in StructuralComponentDatabase.")
        return cls.MOUNTS_AND_TRAYS[component_id]

