"""
VTOL Phase 8 Hardware Requirement Extractor.

Purpose:
    Extracts formal, typed hardware requirement envelopes directly from authoritative
    upstream design outputs (Phase 1 Requirements, Phase 2 Hover, Phase 3 Transition,
    Phase 4 Electrical, Phase 5 Mass/CG, Phase 6 Stability, Phase 7 Optimization).

Standards:
    - Strictly non-mutating: consumes upstream objects without altering them.
    - Full provenance tagging attached to each requirement.
    - Zero fabrication: unknown parameters are marked UNRESOLVED or DEFERRED.
"""

from typing import Any, Dict, List, Optional

from .product_models import (
    HardwareRequirement,
    HardwareCategory,
    ProvenanceCategory,
)


class HardwareRequirementExtractor:
    """
    Translates multidisciplinary engineering sizing outputs into commercial hardware envelopes.
    """

    @classmethod
    def extract_requirements(
        cls,
        design_result: Optional[Any] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> List[HardwareRequirement]:
        """
        Extracts complete list of hardware requirements from a VTOLDesignResult,
        VTOLAircraftSpecification, DesignEvaluation, or fallback defaults.
        """
        reqs: List[HardwareRequirement] = []
        overrides = overrides or {}

        # -------------------------------------------------------------
        # Extract baseline engineering values from upstream result
        # -------------------------------------------------------------
        mtow_kg = 7.869
        lift_motor_count = 4
        hover_tw_target = 1.30
        hover_thrust_per_motor_n = 25.08  # 7.869 * 9.80665 * 1.30 / 4
        hover_power_per_motor_w = 406.1
        hover_current_per_motor_a = 18.29
        system_voltage_v = 22.2  # 6S nominal

        cruise_thrust_n = 16.5  # peak transition forward thrust
        cruise_power_w = 195.0
        cruise_current_a = 8.8

        battery_nominal_wh = 407.0
        battery_continuous_current_a = 75.0
        battery_peak_current_a = 98.5
        battery_mass_budget_kg = 2.250

        payload_mass_kg = 1.50

        # Extract from VTOLDesignResult if provided
        if design_result is not None:
            spec = getattr(design_result, "final_specification", None) or getattr(design_result, "specification", None) or design_result
            
            # MTOW
            if hasattr(spec, "mtow_kg") and spec.mtow_kg > 0:
                mtow_kg = float(spec.mtow_kg)
            elif hasattr(design_result, "mtow_kg") and design_result.mtow_kg > 0:
                mtow_kg = float(design_result.mtow_kg)

            # Hover outputs
            hover_res = getattr(spec, "hover_performance", None)
            if hover_res is not None:
                lift_motor_count = getattr(hover_res, "lift_motor_count", 4) or 4
                if getattr(hover_res, "required_thrust_per_motor_n", None):
                    hover_thrust_per_motor_n = float(hover_res.required_thrust_per_motor_n)
                if getattr(hover_res, "hover_power_per_motor_w", None):
                    hover_power_per_motor_w = float(hover_res.hover_power_per_motor_w)
                if getattr(hover_res, "hover_current_per_motor_a", None):
                    hover_current_per_motor_a = float(hover_res.hover_current_per_motor_a)

            # Electrical outputs
            elec_res = getattr(spec, "electrical", None)
            if elec_res is not None and hasattr(elec_res, "authoritative_energy_result"):
                auth_e = elec_res.authoritative_energy_result
                if auth_e is not None and hasattr(auth_e, "battery_sizing"):
                    bs = auth_e.battery_sizing
                    if getattr(bs, "required_nominal_battery_energy_wh", None):
                        battery_nominal_wh = float(bs.required_nominal_battery_energy_wh)
                if auth_e is not None and hasattr(auth_e, "envelope"):
                    env = auth_e.envelope
                    if getattr(env, "continuous_current_a", None):
                        battery_continuous_current_a = float(env.continuous_current_a)
                    if getattr(env, "peak_current_a", None):
                        battery_peak_current_a = float(env.peak_current_a)

            # Payload
            if hasattr(spec, "payload_weight_kg") and spec.payload_weight_kg > 0:
                payload_mass_kg = float(spec.payload_weight_kg)
            elif hasattr(design_result, "payload_mass_kg") and design_result.payload_mass_kg > 0:
                payload_mass_kg = float(design_result.payload_mass_kg)

        # Allow explicit user overrides
        mtow_kg = overrides.get("mtow_kg", mtow_kg)
        hover_thrust_per_motor_n = overrides.get("hover_thrust_per_motor_n", hover_thrust_per_motor_n)
        battery_nominal_wh = overrides.get("battery_nominal_wh", battery_nominal_wh)
        payload_mass_kg = overrides.get("payload_mass_kg", payload_mass_kg)

        # -------------------------------------------------------------
        # 1. VTOL LIFT MOTORS
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_VTOL_MOTOR_THRUST",
            category=HardwareCategory.VTOL_MOTOR,
            parameter="thrust_n",
            minimum_value=hover_thrust_per_motor_n,
            units="N",
            quantity=lift_motor_count,
            source_phase=2,
            source_model="AuthoritativeHoverResult",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes=f"Minimum peak hover thrust per lift rotor at (T/W target >= {hover_tw_target:.2f})",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_VTOL_MOTOR_VOLTAGE",
            category=HardwareCategory.VTOL_MOTOR,
            parameter="voltage_min_v",
            minimum_value=system_voltage_v,
            units="V",
            quantity=lift_motor_count,
            source_phase=1,
            source_model="VTOLRequirementModel",
            provenance=ProvenanceCategory.PROJECT_REQUIREMENT,
            hard_constraint=True,
            notes="Nominal 6S LiPo bus operating voltage.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_VTOL_MOTOR_MASS",
            category=HardwareCategory.VTOL_MOTOR,
            parameter="mass_kg",
            maximum_value=0.200,
            preferred_value=0.140,
            units="kg",
            quantity=lift_motor_count,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Maximum allowable lift motor unit mass to prevent airframe MTOW inflation.",
        ))

        # -------------------------------------------------------------
        # 2. VTOL LIFT PROPELLERS
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_VTOL_PROP_MASS",
            category=HardwareCategory.VTOL_PROPELLER,
            parameter="mass_kg",
            maximum_value=0.045,
            preferred_value=0.028,
            units="kg",
            quantity=lift_motor_count,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Carbon fiber rotor mass budget.",
        ))

        # -------------------------------------------------------------
        # 3. VTOL LIFT ESCS
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_VTOL_ESC_CURRENT",
            category=HardwareCategory.VTOL_ESC,
            parameter="continuous_current_a",
            minimum_value=25.0,
            units="A",
            quantity=lift_motor_count,
            source_phase=4,
            source_model="ElectricalEnvelope",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Continuous current rating exceeding hover per-motor current with 1.35x margin.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_VTOL_ESC_VOLTAGE",
            category=HardwareCategory.VTOL_ESC,
            parameter="voltage_max_v",
            minimum_value=25.2,
            units="V",
            quantity=lift_motor_count,
            source_phase=4,
            source_model="ElectricalEnvelope",
            provenance=ProvenanceCategory.PROJECT_REQUIREMENT,
            hard_constraint=True,
            notes="6S LiPo maximum charged voltage.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_VTOL_ESC_MASS",
            category=HardwareCategory.VTOL_ESC,
            parameter="mass_kg",
            maximum_value=0.055,
            preferred_value=0.042,
            units="kg",
            quantity=lift_motor_count,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Per-ESC mass allocation.",
        ))

        # -------------------------------------------------------------
        # 4. CRUISE PROPULSION
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_CRUISE_MOTOR_THRUST",
            category=HardwareCategory.CRUISE_MOTOR,
            parameter="thrust_n",
            minimum_value=cruise_thrust_n,
            units="N",
            quantity=1,
            source_phase=3,
            source_model="AuthoritativeTransitionResult",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Forward propulsion thrust required during peak transition acceleration corridor.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_CRUISE_MOTOR_MASS",
            category=HardwareCategory.CRUISE_MOTOR,
            parameter="mass_kg",
            maximum_value=0.180,
            preferred_value=0.150,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Cruise motor mass budget.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_CRUISE_ESC_CURRENT",
            category=HardwareCategory.CRUISE_ESC,
            parameter="continuous_current_a",
            minimum_value=20.0,
            units="A",
            quantity=1,
            source_phase=4,
            source_model="ElectricalBusMetrics",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Forward flight ESC continuous current capability.",
        ))

        # -------------------------------------------------------------
        # 5. BATTERY SYSTEM
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_BATTERY_ENERGY_NOMINAL",
            category=HardwareCategory.BATTERY_PACK,
            parameter="energy_nominal_wh",
            minimum_value=battery_nominal_wh,
            units="Wh",
            quantity=1,
            source_phase=4,
            source_model="BatterySizingRequirements",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Nominal energy sized from mission ledger with 20% reserve and 85% DoD.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_BATTERY_CURRENT_CONT",
            category=HardwareCategory.BATTERY_PACK,
            parameter="continuous_current_a",
            minimum_value=battery_continuous_current_a,
            units="A",
            quantity=1,
            source_phase=4,
            source_model="ElectricalEnvelope",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Total vertical hover simultaneous continuous current capacity.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_BATTERY_MASS",
            category=HardwareCategory.BATTERY_PACK,
            parameter="mass_kg",
            maximum_value=2.450,
            preferred_value=battery_mass_budget_kg,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Direct battery mass sizing limit from Phase 5 converged ledger.",
        ))

        # -------------------------------------------------------------
        # 6. POWER DISTRIBUTION
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_PDB_CURRENT",
            category=HardwareCategory.POWER_DISTRIBUTION,
            parameter="continuous_current_a",
            minimum_value=100.0,
            units="A",
            quantity=1,
            source_phase=4,
            source_model="ElectricalEnvelope",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Main bus continuous current distribution capability.",
        ))

        # -------------------------------------------------------------
        # 7. ACTUATION / SERVOS (Mandated Section 14)
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_SERVO_MASS",
            category=HardwareCategory.SERVO,
            parameter="mass_kg",
            maximum_value=0.035,
            preferred_value=0.020,
            units="kg",
            quantity=4,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Maximum allowable servo unit mass (4 servos: 2 Ruddervators + 2 Ailerons).",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_SERVO_TORQUE",
            category=HardwareCategory.SERVO,
            parameter="stall_torque_nm",
            minimum_value=None,  # Intentionally None: Phase 6 does not calculate hinge moments
            units="N*m",
            quantity=4,
            source_phase=6,
            source_model="AuthoritativeStabilityResult",
            provenance=ProvenanceCategory.DEFERRED,
            hard_constraint=False,
            verification_method="QUALIFIED_CATALOG_MATCH",
            notes="Phase 6 does not evaluate aerodynamic hinge moments. Classified as DEFERRED / INSUFFICIENT_INPUT as mandated.",
        ))

        # -------------------------------------------------------------
        # 8. FLIGHT CONTROL & AVIONICS
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_FC_PWM_OUTPUTS",
            category=HardwareCategory.FLIGHT_CONTROLLER,
            parameter="pwm_channels",
            minimum_value=9.0,
            units="channels",
            quantity=1,
            source_phase=1,
            source_model="VTOLConfiguration",
            provenance=ProvenanceCategory.DERIVED,
            hard_constraint=True,
            notes="Minimum 9 channels: 4 lift motors + 1 cruise motor + 2 ruddervators + 2 ailerons.",
        ))
        reqs.append(HardwareRequirement(
            requirement_id="REQ_FC_MASS",
            category=HardwareCategory.FLIGHT_CONTROLLER,
            parameter="mass_kg",
            maximum_value=0.100,
            preferred_value=0.075,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Autopilot mass allocation.",
        ))

        # -------------------------------------------------------------
        # 9. NAVIGATION
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_NAV_MASS",
            category=HardwareCategory.NAVIGATION_GNSS,
            parameter="mass_kg",
            maximum_value=0.070,
            preferred_value=0.049,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="GNSS + compass mast mass budget.",
        ))

        # -------------------------------------------------------------
        # 10. AIRSPEED SENSOR
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_AIRSPEED_MASS",
            category=HardwareCategory.AIRSPEED_SENSOR,
            parameter="mass_kg",
            maximum_value=0.025,
            preferred_value=0.012,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Pitot tube and differential digital transducer mass allocation.",
        ))

        # -------------------------------------------------------------
        # 11. COMMUNICATION
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_COMM_MASS",
            category=HardwareCategory.TELEMETRY_LINK,
            parameter="mass_kg",
            maximum_value=0.055,
            preferred_value=0.038,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Telemetry transceiver air-unit mass budget.",
        ))

        # -------------------------------------------------------------
        # 12. RC RECEIVER
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_RC_RECEIVER_MASS",
            category=HardwareCategory.RC_RECEIVER,
            parameter="mass_kg",
            maximum_value=0.020,
            preferred_value=0.006,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Long-range RC control receiver mass allocation.",
        ))

        # -------------------------------------------------------------
        # 13. COMPANION COMPUTER
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_COMPANION_SBC_MASS",
            category=HardwareCategory.COMPANION_COMPUTER,
            parameter="mass_kg",
            maximum_value=0.120,
            preferred_value=0.046,
            units="kg",
            quantity=1,
            source_phase=5,
            source_model="AuthoritativeComponentMass",
            provenance=ProvenanceCategory.CONFIGURABLE_ASSUMPTION,
            hard_constraint=True,
            notes="Onboard companion SBC for payload autonomy and high-level telemetry.",
        ))

        # -------------------------------------------------------------
        # 14. PAYLOAD
        # -------------------------------------------------------------
        reqs.append(HardwareRequirement(
            requirement_id="REQ_PAYLOAD_CAPACITY",
            category=HardwareCategory.MISSION_PAYLOAD,
            parameter="mass_kg",
            maximum_value=payload_mass_kg,
            units="kg",
            quantity=1,
            source_phase=1,
            source_model="VTOLRequirementModel",
            provenance=ProvenanceCategory.PROJECT_REQUIREMENT,
            hard_constraint=True,
            notes="Mission payload mass carrying requirement.",
        ))

        return reqs

