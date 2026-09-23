"""
AssemblySequence Subsystem

Purpose:
    Defines the `AssemblySequence` class for computing subassembly order dependencies.

Role in Architecture:
    `AssemblySequence` generates the assembly step-by-step instructions (Frame -> Propulsion -> Electrical -> Avionics -> Payload -> Final Calibration).
"""

from typing import Any
from backend.design.drone.manufacturing.assembly_plan import AssemblyPlan


class AssemblySequence:
    """
    Subassembly order and instructions sequence planner.

    Design Principles:
        - Single Responsibility Principle: Sequential assembly instruction generation only.
    """

    def generate_sequence(self) -> list[dict[str, Any]]:
        """
        Generates step-by-step assembly instructions.

        Returns:
            list[dict[str, Any]]: Assembly steps sequence list.
        """
        return [
            {
                "step": 1,
                "title": "Airframe Center Plate & Landing Gear Assembly",
                "instructions": "Mount landing gear tubes to the carbon fiber center plates using M3 bolts. Apply blue threadlocker.",
                "torque_n_m": 1.2
            },
            {
                "step": 2,
                "title": "Arm Tube Installation",
                "instructions": "Insert carbon fiber arms into center plate clamps. Tighten M4 bolts symmetrically.",
                "torque_n_m": 2.0
            },
            {
                "step": 3,
                "title": "Propulsion Motor Mounting",
                "instructions": "Bolt BLDC motors onto the arm carbon mounts. Feed motor phase wires inside carbon tubes.",
                "torque_n_m": 1.5
            },
            {
                "step": 4,
                "title": "Electrical Power & ESC Routing",
                "instructions": "Solder motor wires to ESC outputs. Connect ESC inputs to PDB outputs. Connect main battery lead.",
                "torque_n_m": 0.0
            },
            {
                "step": 5,
                "title": "Avionics Flight Controller Mounting",
                "instructions": "Place flight controller on anti-vibration damping mount. Connect GPS, telemetry radio, and receiver.",
                "torque_n_m": 0.5
            },
            {
                "step": 6,
                "title": "Payload Integration & Mount",
                "instructions": "Attach gimbal mount to bottom center accessory rails. Slide quick release payload tray in.",
                "torque_n_m": 1.0
            }
        ]
