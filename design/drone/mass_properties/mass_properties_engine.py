"""
MassPropertiesEngine Subsystem

Purpose:
    Defines the `MassPropertiesEngine` class, which serves as the public entry point for multirotor mass properties and CG analysis.

Role in Architecture:
    `MassPropertiesEngine` aggregates component mass models across all designed subsystems (`StructureResult`, `PropulsionResult`,
    `ElectricalResult`, `AvionicsResult`, `PayloadResult`), computes 3D Center of Gravity, Moments of Inertia, static balance,
    validates MTOW and balance bounds, and returns a `MassResult`.
"""

import math
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.mass_properties.component_mass import ComponentMass
from backend.design.drone.mass_properties.mass_breakdown import MassBreakdownCalculator
from backend.design.drone.mass_properties.center_of_gravity import CenterOfGravityCalculator
from backend.design.drone.mass_properties.moment_of_inertia import MomentOfInertiaCalculator
from backend.design.drone.mass_properties.balance_analysis import BalanceAnalysis
from backend.design.drone.mass_properties.mass_validator import MassValidator
from backend.design.drone.mass_properties.mass_result import MassResult


class MassPropertiesEngine:
    """
    Public entry point service for multirotor mass properties & Center of Gravity analysis.

    Design Principles:
        - Single Responsibility Principle: Subsystem mass aggregation, 3D CG, MoI tensor, and static balance evaluation only.
        - Dependency Injection: Injects calculator and validator collaborators.
        - Non-Redesign: Evaluates existing designed subsystems without modifying subsystem parameters.
    """

    def __init__(
        self,
        breakdown_calc: MassBreakdownCalculator | None = None,
        cg_calc: CenterOfGravityCalculator | None = None,
        moi_calc: MomentOfInertiaCalculator | None = None,
        balance_analysis: BalanceAnalysis | None = None,
        validator: MassValidator | None = None
    ) -> None:
        """Initializes the MassPropertiesEngine."""
        self._breakdown_calc = breakdown_calc if breakdown_calc else MassBreakdownCalculator()
        self._cg_calc = cg_calc if cg_calc else CenterOfGravityCalculator()
        self._moi_calc = moi_calc if moi_calc else MomentOfInertiaCalculator()
        self._balance_analysis = balance_analysis if balance_analysis else BalanceAnalysis()
        self._validator = validator if validator else MassValidator()

    def analyze_mass_properties(
        self,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        max_mtow_kg: float = 25.0
    ) -> MassResult:
        """
        Computes total mass properties, mass breakdown, 3D CG, Moments of Inertia, and static balance.

        Args:
            structure_result (FrameResult): Structural airframe result.
            propulsion_result (PropulsionResult): Propulsion subsystem result.
            electrical_result (ElectricalResult): Electrical power result.
            avionics_result (AvionicsResult): Avionics subsystem result.
            payload_result (PayloadResult): Mission payload result.
            max_mtow_kg (float): Maximum MTOW limit in kg.

        Returns:
            MassResult: Completed mass properties and CG engineering result.
        """
        components: list[ComponentMass] = []

        # 1. Structure
        frame_g = structure_result.selected_frame.frame_weight_g
        components.append(ComponentMass("Bare Frame Structure", "STRUCTURE", frame_g, 0.0, 0.0, 0.0))

        # 2. Landing Gear
        gear_g = structure_result.landing_gear.weight_g
        gear_z = - structure_result.landing_gear.height_mm / 2.0
        components.append(ComponentMass("Landing Gear Assembly", "LANDING_GEAR", gear_g, 0.0, 0.0, gear_z))

        # 3. Motors & Propellers
        rotor_count = propulsion_result.selected_motors.get("rotor_count", 4)
        m_weight = propulsion_result.selected_motors.get("estimated_motor_weight_g", 55.0)
        p_weight = propulsion_result.selected_propellers.get("weight_per_prop_g", 10.0)
        arm_len = structure_result.arm_geometry.arm_length_mm

        for i in range(rotor_count):
            angle = (2.0 * math.pi * i) / (rotor_count // 2 if propulsion_result.selected_motors.get("coaxial", False) else rotor_count)
            mx = arm_len * math.cos(angle)
            my = arm_len * math.sin(angle)
            mz = 15.0 if (i % 2 == 0 or not propulsion_result.selected_motors.get("coaxial", False)) else -15.0
            components.append(ComponentMass(f"Motor & Prop {i+1}", "PROPULSION", m_weight + p_weight, mx, my, mz))

        # 4. Electrical
        bat_g = electrical_result.selected_battery.get("estimated_battery_weight_g", 600.0)
        components.append(ComponentMass("Battery Pack", "ELECTRICAL", bat_g, 0.0, 0.0, -40.0))

        esc_g = electrical_result.selected_escs.get("total_esc_weight_g", 40.0)
        components.append(ComponentMass("ESC Unit / Assembly", "ELECTRICAL", esc_g, 0.0, 0.0, 0.0))

        pdb_g = electrical_result.selected_pdb.get("weight_g", 15.0) + electrical_result.selected_bec.get("weight_g", 12.0)
        components.append(ComponentMass("PDB & BEC Module", "ELECTRICAL", pdb_g, 0.0, 0.0, 10.0))

        conn_g = electrical_result.selected_connectors.get("connector_weight_g", 15.0) + 25.0  # wires
        components.append(ComponentMass("Wiring & Connectors", "ELECTRICAL", conn_g, 0.0, 0.0, -20.0))

        # 5. Avionics
        fc_g = avionics_result.power_analysis.total_avionics_weight_g
        components.append(ComponentMass("Avionics Suite (FC, GNSS, Telem, RX)", "AVIONICS", fc_g, 0.0, 0.0, 20.0))

        # 6. Payload
        pay_g = payload_result.selected_payload.mass_kg * 1000.0
        pay_x = payload_result.balance_analysis.cg_offset_x_mm
        pay_y = payload_result.balance_analysis.cg_offset_y_mm
        pay_z = - payload_result.balance_analysis.cg_offset_z_mm
        components.append(ComponentMass("Mission Payload & Mount", "PAYLOAD", pay_g, pay_x, pay_y, pay_z))

        # 7. Fasteners & Margins (5% each)
        subtotal_g = sum(c.mass_g for c in components)
        fastener_g = round(subtotal_g * 0.05, 1)
        margin_g = round(subtotal_g * 0.05, 1)

        components.append(ComponentMass("Fasteners & Hardware", "FASTENERS", fastener_g, 0.0, 0.0, 0.0))
        components.append(ComponentMass("Engineering Growth Margin", "MARGIN", margin_g, 0.0, 0.0, 0.0))

        # Calculate Mass Breakdown, CG, MoI, and Balance Analysis
        breakdown = self._breakdown_calc.calculate_breakdown(components)
        cg = self._cg_calc.calculate_cg(components)
        moi = self._moi_calc.calculate_moi(components, cg)
        balance = self._balance_analysis.analyze_balance(cg, breakdown.total_mass_g / 1000.0, bat_g / 1000.0)

        result = MassResult(
            total_mass_kg=round(breakdown.total_mass_g / 1000.0, 2),
            empty_mass_kg=round(breakdown.empty_mass_g / 1000.0, 2),
            payload_mass_kg=round(breakdown.payload_mass_g / 1000.0, 2),
            mass_breakdown=breakdown,
            center_of_gravity=cg,
            moment_of_inertia=moi,
            balance_analysis=balance,
            engineering_notes=f"Complete mass properties analysis: AUW {breakdown.total_mass_g / 1000.0:.2f} kg, CG X={cg.cg_x_mm:.1f}mm, Y={cg.cg_y_mm:.1f}mm, Z={cg.cg_z_mm:.1f}mm."
        )

        warns = self._validator.validate_mass_properties(result, max_mtow_kg)
        if warns:
            result.warnings.extend(warns)

        return result
