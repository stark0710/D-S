"""
VTOL Configuration Engine Subsystem

Purpose:
    Defines the `ConfigurationEngine` orchestrator coordinating layout selection,
    actuator spacing, flight mode configurations, and trade-off scoring.
"""

from typing import List, Dict, Any
from datetime import datetime

from backend.design.vtol.mission.mission_requirements import VTOLType
from backend.design.vtol.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.vtol.configuration.configuration_profile import ConfigurationProfile
from backend.design.vtol.configuration.configuration_result import ConfigurationResult
from backend.design.vtol.configuration.configuration_validator import ConfigurationValidator
from backend.design.vtol.configuration.configuration_registry import VTOLConfigurationStrategyRegistry
from backend.design.vtol.configuration.configuration_selector import ConfigurationSelector
from backend.design.vtol.configuration.layout_generator import LayoutGenerator
from backend.design.vtol.configuration.propulsion_layout import PropulsionLayout
from backend.design.vtol.configuration.actuator_layout import ActuatorLayout
from backend.design.vtol.configuration.flight_mode_configuration import FlightMode, FlightModeConfiguration
from backend.design.vtol.configuration.configuration_analysis import ConfigurationAnalysis
from backend.design.vtol.configuration.vtol_configuration import VTOLConfiguration


class ConfigurationEngine:
    """
    Facade orchestrator driving configuration trade-off checks, actuator layout
    mapping, and mode config definitions.
    """

    def __init__(
        self,
        validator: ConfigurationValidator | None = None,
        selector: ConfigurationSelector | None = None,
        layout_gen: LayoutGenerator | None = None,
    ) -> None:
        self._validator = validator or ConfigurationValidator()
        self._selector = selector or ConfigurationSelector()
        self._layout_gen = layout_gen or LayoutGenerator()

    def design_configuration(self, requirements: ConfigurationRequirements) -> ConfigurationResult:
        """
        Processes configuration inputs and yields the sized spatial layout and analysis.

        Args:
            requirements (ConfigurationRequirements): Configuration sizing inputs.

        Returns:
            ConfigurationResult: Complete structural configuration.
        """
        # 1. Validate requirements
        self._validator.validate(requirements)

        # 2. Strategy selection
        mission_res = requirements.mission_result
        strategy = VTOLConfigurationStrategyRegistry.get(mission_res.mission_profile.mission_category)

        # 3. Select optimal layout architecture
        selected_layout, candidate_scores = self._selector.select_best_layout(requirements, strategy)

        # 4. Generate spatial geometry and coordinates
        mtow = mission_res.mission_analysis.estimated_mtow_kg
        layout_data = self._layout_gen.generate_layout(selected_layout, mtow, requirements.desired_motor_count)

        # 5. Populate Propulsion Layouts
        # Dedicated lift details
        if selected_layout in (VTOLType.TILT_ROTOR, VTOLType.TILT_WING):
            lift_style = "Tilt Rotor Vectoring"
            fwd_style = "Tilt Rotor Forward Vector"
        elif selected_layout == VTOLType.TAIL_SITTER:
            lift_style = "Differential Main Rotors"
            fwd_style = "Direct Main Propulsion"
        elif selected_layout == VTOLType.LIFT_CRUISE:
            lift_style = "Dedicated Multi-rotor Booms"
            fwd_style = "Rear Pusher Propeller"
        elif selected_layout == VTOLType.QUADPLANE:
            lift_style = "Standard Quadcopter Arms"
            fwd_style = "Front Tractor Propeller"
        else:
            lift_style = "Custom Lift Setup"
            fwd_style = "Custom Cruise Setup"

        lift_arch = PropulsionLayout(
            lift_system_type=lift_style,
            forward_propulsion_layout=fwd_style,
            motor_count=layout_data["lift_motor_count"],
            propeller_count=layout_data["lift_motor_count"],
            has_pitch_control=requirements.metadata.get("variable_pitch_lift", False),
            is_hybrid=requirements.metadata.get("hybrid_lift_system", False),
            mounting_structure="Composite motor booms" if selected_layout != VTOLType.TAIL_SITTER else "Main wing engine pods",
        )

        fwd_arch = PropulsionLayout(
            lift_system_type=lift_style,
            forward_propulsion_layout=fwd_style,
            motor_count=layout_data["forward_motor_count"],
            propeller_count=layout_data["forward_motor_count"],
            has_pitch_control=requirements.metadata.get("variable_pitch_cruise", False),
            is_hybrid=requirements.metadata.get("hybrid_cruise_system", False),
            mounting_structure="Fuselage firewalls" if selected_layout != VTOLType.TAIL_SITTER else "Main wing motor mounts",
        )

        # 6. Populate Actuator Layout
        actuator_lay = ActuatorLayout(
            control_channels_count=layout_data["control_channels_count"],
            servo_count=layout_data["servo_count"],
            esc_count=layout_data["esc_count"],
            aerodynamic_surface_actuators=layout_data["aerodynamic_surface_actuators"],
            propulsion_actuators=layout_data["propulsion_actuators"],
            tilt_actuators=layout_data["tilt_actuators"],
            actuator_placements=layout_data["actuator_placements"],
        )

        # 7. Flight Mode configuration
        trans_speed = mission_res.transition_requirements.transition_speed_kmh
        cruise_speed = mission_res.cruise_requirements.cruise_speed_kmh

        flight_mode_config = FlightModeConfiguration(
            hover=FlightMode(
                name="Hover",
                is_active=True,
                thrust_allocation="Lift Motors",
                attitude_control="Differential thrust and torque",
                target_speed_range_kmh=(0.0, 15.0),
                description="Zero forward velocity vertical stabilization.",
            ),
            takeoff=FlightMode(
                name="Vertical Takeoff",
                is_active=True,
                thrust_allocation="Lift Motors Climb",
                attitude_control="Diff thrust control loop",
                target_speed_range_kmh=(0.0, 10.0),
                description="Autonomous vertical ascent to transition altitude.",
            ),
            landing=FlightMode(
                name="Vertical Landing",
                is_active=True,
                thrust_allocation="Lift Motors Descent",
                attitude_control="Diff thrust control loop",
                target_speed_range_kmh=(0.0, 10.0),
                description="Precision landing descent onto takeoff waypoint.",
            ),
            transition_to_cruise=FlightMode(
                name="Transition to Cruise",
                is_active=True,
                thrust_allocation="Blended Lift and Cruise",
                attitude_control="Diff thrust + Aerodynamic surfaces",
                target_speed_range_kmh=(15.0, trans_speed),
                description="Accelerating and transferring lift from rotors to wing.",
            ),
            cruise=FlightMode(
                name="Cruise",
                is_active=True,
                thrust_allocation="Cruise Propellers",
                attitude_control="Aerodynamic surfaces",
                target_speed_range_kmh=(trans_speed, cruise_speed * 1.2),
                description="Efficient wing-borne forward flight.",
            ),
            transition_to_hover=FlightMode(
                name="Transition to Hover",
                is_active=True,
                thrust_allocation="Blended / Decelerating",
                attitude_control="Diff thrust + Aerodynamic surfaces",
                target_speed_range_kmh=(15.0, trans_speed),
                description="Decelerating forward flight to stall and vertical capture.",
            ),
            emergency=FlightMode(
                name="Emergency Mode",
                is_active=True,
                thrust_allocation="Max Sized Recovery Thrust / Passive Glide",
                attitude_control="Fail-safe surface actuators",
                target_speed_range_kmh=(0.0, cruise_speed * 1.3),
                description="Autopilot triggers parachutes or high-power hover recoveries.",
            ),
            recovery=FlightMode(
                name="Recovery Mode",
                is_active=True,
                thrust_allocation="Failsafe Return Flight",
                attitude_control="Assisted stabilization",
                target_speed_range_kmh=(0.0, cruise_speed),
                description="Safe home flight profile under degraded sensor states.",
            ),
        )

        # 8. Sizing trade-offs and analysis
        # Build baseline trade-offs depending on chosen layout
        if selected_layout == VTOLType.QUADPLANE:
            hover_eff = 80.0
            cruise_eff = 65.0
            trans_comp = 40.0
            struct_simp = 85.0
            mfg = 90.0
            redundancy = 70.0
            maint = 85.0
            scale_score = 75.0
        elif selected_layout in (VTOLType.TILT_ROTOR, VTOLType.TILT_WING):
            hover_eff = 78.0
            cruise_eff = 88.0
            trans_comp = 85.0
            struct_simp = 50.0
            mfg = 60.0
            redundancy = 60.0
            maint = 55.0
            scale_score = 80.0
        elif selected_layout == VTOLType.LIFT_CRUISE:
            hover_eff = 85.0
            cruise_eff = 70.0
            trans_comp = 45.0
            struct_simp = 80.0
            mfg = 85.0
            redundancy = 85.0
            maint = 80.0
            scale_score = 75.0
        elif selected_layout == VTOLType.TAIL_SITTER:
            hover_eff = 72.0
            cruise_eff = 92.0
            trans_comp = 90.0
            struct_simp = 90.0
            mfg = 80.0
            redundancy = 50.0
            maint = 75.0
            scale_score = 60.0
        else:  # Custom/Twin Boom/etc
            hover_eff = 75.0
            cruise_eff = 75.0
            trans_comp = 60.0
            struct_simp = 70.0
            mfg = 75.0
            redundancy = 70.0
            maint = 70.0
            scale_score = 70.0

        # Adjust redundancy score if user specified redundant counts
        if requirements.redundancy_requirement == "Single Motor Out":
            redundancy = max(redundancy, 85.0)

        # Suitability score matches the selected candidate selector score
        suitability = candidate_scores.get(selected_layout, 75.0)

        analysis = ConfigurationAnalysis(
            mission_suitability=suitability,
            hover_efficiency=hover_eff,
            cruise_efficiency=cruise_eff,
            transition_complexity=trans_comp,
            structural_simplicity=struct_simp,
            manufacturability=mfg,
            redundancy_score=redundancy,
            maintenance_accessibility=maint,
            scalability=scale_score,
            metadata={"candidate_scores": {k.value: v for k, v in candidate_scores.items()}},
        )

        # 9. Recommendations, Warnings, Notes
        notes = [
            f"Configuration Engine selected architecture: {selected_layout.value}.",
            f"Required ESC output signals sized: {actuator_lay.esc_count}.",
            f"Required servo control surfaces channels: {actuator_lay.servo_count}.",
            f"Total avionics control channels allocated: {actuator_lay.control_channels_count}.",
        ]

        # Construct the ConfigurationProfile
        has_wings = selected_layout not in (VTOLType.CUSTOM,)
        has_tail = selected_layout in (
            VTOLType.QUADPLANE,
            VTOLType.LIFT_CRUISE,
            VTOLType.TILT_ROTOR,
            VTOLType.TILT_WING,
            VTOLType.TWIN_BOOM_VTOL,
        )
        has_tilt = selected_layout in (VTOLType.TILT_ROTOR, VTOLType.TILT_WING)

        profile = ConfigurationProfile(
            vtol_type=selected_layout,
            motor_count=layout_data["motor_count"],
            lift_motor_count=layout_data["lift_motor_count"],
            forward_motor_count=layout_data["forward_motor_count"],
            has_wings=has_wings,
            has_tail=has_tail,
            has_tilt=has_tilt,
            redundancy_level=requirements.redundancy_requirement,
            metadata={"layout_data": layout_data},
        )

        recs = strategy.get_recommendations(profile)
        if selected_layout == VTOLType.TAIL_SITTER:
            recs.append("Verify control surface sizes are large enough to deflect prop wash during hover.")
        if selected_layout in (VTOLType.TILT_ROTOR, VTOLType.TILT_WING):
            recs.append("Ensure metal-geared high-torque servos are specified for tilt pivot tubes.")

        warnings: List[str] = []
        if actuator_lay.control_channels_count > 16:
            warnings.append("Control channel count exceeds standard 16. Requires dual-receiver or bus-expanded decoders.")
        if selected_layout == VTOLType.TAIL_SITTER and mtow > 12.0:
            warnings.append("Heavy Tail Sitter configurations are susceptible to landing tip-overs in high winds.")

        meta = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.__class__.__name__,
            "configuration_profile": profile,
        }

        # Authoritative VTOLConfiguration
        if selected_layout == VTOLType.QUADPLANE:
            vtol_config = VTOLConfiguration.create_quadplane_default(motor_count=layout_data["lift_motor_count"])
        elif selected_layout == VTOLType.LIFT_CRUISE:
            vtol_config = VTOLConfiguration.create_lift_cruise_default(
                lift_motor_count=layout_data["lift_motor_count"],
                cruise_motor_count=layout_data["forward_motor_count"],
            )
        else:
            vtol_config = VTOLConfiguration(
                configuration_type=selected_layout,
                lift_motor_count=layout_data["lift_motor_count"],
                lift_rotor_count=layout_data["lift_motor_count"],
                cruise_propulsion_count=layout_data["forward_motor_count"],
                propulsion_arrangement=f"{layout_data['lift_motor_count']}_lift_plus_{layout_data['forward_motor_count']}_forward",
            )

        return ConfigurationResult(
            selected_configuration=selected_layout,
            lift_architecture=lift_arch,
            forward_propulsion_layout=fwd_arch,
            flight_mode_configuration=flight_mode_config,
            actuator_layout=actuator_lay,
            configuration_analysis=analysis,
            vtol_configuration=vtol_config,
            engineering_notes=notes,
            recommendations=recs,
            warnings=warnings,
            metadata=meta,
        )
