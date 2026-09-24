from typing import Any, Dict, Tuple
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.multirotor.mission.mission_profile import MissionProfile
from backend.design.multirotor.mission.mission_constraints import MissionConstraints
from backend.design.multirotor.mission.mission_targets import MissionTargets
from backend.design.multirotor.mission.strategy_models import PriorityWeights, DesignStrategy
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification
from backend.design.multirotor.mission.mission_validator import MissionValidator

class MissionStrategyEngine:
    """
    Translates high-level multirotor mission requirements into physical constraints,
    optimization priority weights, and target metrics for downstream sizers.
    """
    def __init__(self, validator: MissionValidator | None = None) -> None:
        self._validator = validator if validator else MissionValidator()

    def generate_strategy(self, requirements: RequirementModel) -> MissionStrategySpecification:
        """
        Translates a RequirementModel into a complete MissionStrategySpecification.
        """
        # 1. Run validation checks
        self._validator.validate(requirements)

        # 2. Extract and normalize mission profile parameters
        mission_raw = requirements.mission_type
        mission_str = ""
        if isinstance(mission_raw, MissionType):
            mission_str = mission_raw.value.lower()
        elif isinstance(mission_raw, str):
            mission_str = mission_raw.lower()

        # If it is CUSTOM, check metadata
        if mission_str == "custom" or mission_str == "custom_mission":
            metadata_type = requirements.metadata.get("multirotor_mission", "")
            if isinstance(metadata_type, str) and metadata_type:
                mission_str = metadata_type.lower()

        payload_weight = requirements.payload_weight_kg
        flight_time = requirements.target_flight_time_min
        range_km = requirements.target_range_km
        speed_kmh = requirements.cruise_speed_kmh

        # Extract environment and default constraints
        env_raw = requirements.environment
        env_str = env_raw.value.lower() if isinstance(env_raw, OperatingEnvironment) else str(env_raw).lower()

        wind_limit = requirements.metadata.get("wind_conditions_kmh")
        if wind_limit is None:
            # Enforce defaults based on operating environment
            if env_str in ["urban", "mountain", "marine"]:
                wind_limit = 25.0
            elif env_str == "forest":
                wind_limit = 20.0
            else:
                wind_limit = 15.0

        budget_val = requirements.budget if requirements.budget is not None else 5000.0
        
        redundancy_val = requirements.metadata.get("redundancy_required")
        if redundancy_val is None:
            # Look at redundancy_required on metadata or set to budget/safety indicator
            redundancy_val = bool(requirements.metadata.get("redundancy", False))

        max_frame = requirements.metadata.get("maximum_frame_size_m", 1.0)
        battery_pref = requirements.metadata.get("battery_preference", "LiPo")
        camera_req = requirements.metadata.get("camera_requirement", "none")
        autonomy = requirements.metadata.get("autonomy_level", "Fully Autonomous")
        payload_dims = requirements.metadata.get("payload_dimensions_m", (0.1, 0.1, 0.1))

        profile = MissionProfile(
            mission_type=mission_str,
            payload_weight_kg=payload_weight,
            payload_dimensions_m=payload_dims,
            target_flight_time_min=flight_time,
            target_range_km=range_km,
            cruise_speed_kmh=speed_kmh,
            operating_environment=env_str,
            wind_conditions_kmh=wind_limit,
            budget=budget_val,
            redundancy_required=redundancy_val,
            maximum_frame_size_m=max_frame,
            battery_preference=battery_pref,
            camera_requirement=camera_req,
            autonomy_level=autonomy,
            metadata=requirements.metadata
        )

        # 3. Create Constraints
        min_clearance = 0.15 if env_str == "rural" else 0.25
        constraints = MissionConstraints(
            maximum_frame_size_m=max_frame,
            wind_resistance_limit_kmh=wind_limit,
            minimum_ground_clearance_m=min_clearance,
            cost_limit_usd=budget_val
        )

        # 4. Resolve priority weights and design strategies based on mission category
        weights, strategy = self._resolve_strategy_rules(mission_str)

        # 5. Resolve recommended configuration
        rec_config = self._resolve_recommended_configuration(payload_weight, redundancy_val)

        # 6. Resolve targets
        targets = self._resolve_engineering_targets(profile, rec_config)

        # Create the spec
        optimization_priorities = {
            "endurance": weights.endurance,
            "payload_capacity": weights.payload_capacity,
            "efficiency": weights.efficiency,
            "agility": weights.agility,
            "wind_resistance": weights.wind_resistance,
            "cost": weights.cost,
            "reliability": weights.reliability,
            "safety": weights.safety,
            "redundancy": weights.redundancy,
            "manufacturability": weights.manufacturability
        }

        mission_summary = {
            "mission_type": mission_str,
            "payload_weight_kg": payload_weight,
            "target_flight_time_min": flight_time,
            "target_range_km": range_km,
            "operating_environment": env_str
        }

        return MissionStrategySpecification(
            mission_summary=mission_summary,
            engineering_targets=targets,
            priority_weights=weights,
            constraint_summary=constraints,
            recommended_configuration_class=rec_config,
            design_strategy=strategy,
            optimization_priorities=optimization_priorities
        )

    def _resolve_strategy_rules(self, mission: str) -> Tuple[PriorityWeights, DesignStrategy]:
        """
        Maps mission classifications to weights and engineering strategies.
        """
        if mission in ["photography", "videography"]:
            weights = PriorityWeights(
                endurance=0.7, payload_capacity=0.5, efficiency=0.6, agility=0.4,
                wind_resistance=0.7, cost=0.6, reliability=0.8, safety=0.8,
                redundancy=0.4, manufacturability=0.7
            )
            strategy = DesignStrategy(
                key_objective="Vibration-free stable image capture",
                propulsion_strategy="High pole count, low KV motors with carbon fiber props for smooth response",
                structural_strategy="Vibration isolation mounts, lightweight carbon fiber frame",
                electrical_strategy="Integrated gimbal supply, low ESR power distribution"
            )
        elif mission in ["survey", "mapping", "inspection", "infrastructure inspection"]:
            weights = PriorityWeights(
                endurance=1.0, payload_capacity=0.6, efficiency=0.9, agility=0.3,
                wind_resistance=0.8, cost=0.5, reliability=0.9, safety=0.8,
                redundancy=0.6, manufacturability=0.7
            )
            strategy = DesignStrategy(
                key_objective="Long-endurance area coverage",
                propulsion_strategy="Low disc loading, high diameter carbon fiber propellers, high-efficiency motors",
                structural_strategy="Stiff carbon fiber monocoque arms, low aerodynamic drag frame",
                electrical_strategy="Li-Ion high specific energy battery pack"
            )
        elif mission in ["cargo delivery", "heavy lift", "delivery"]:
            weights = PriorityWeights(
                endurance=0.5, payload_capacity=1.0, efficiency=0.6, agility=0.4,
                wind_resistance=0.7, cost=0.5, reliability=1.0, safety=1.0,
                redundancy=1.0, manufacturability=0.6
            )
            strategy = DesignStrategy(
                key_objective="Heavy-payload transportation with high redundancy",
                propulsion_strategy="Coaxial X8 or Octocopter topology, high-thrust motors with large safety margin",
                structural_strategy="Reinforced arm joints, high yield stress material construction",
                electrical_strategy="Dual-redundant battery packs, high continuous current bus"
            )
        elif mission in ["search & rescue", "emergency response", "security", "surveillance", "disaster_response", "military"]:
            weights = PriorityWeights(
                endurance=0.8, payload_capacity=0.7, efficiency=0.7, agility=0.7,
                wind_resistance=0.9, cost=0.4, reliability=0.9, safety=0.9,
                redundancy=0.8, manufacturability=0.6
            )
            strategy = DesignStrategy(
                key_objective="All-weather quick-response operational reliability",
                propulsion_strategy="Weather-sealed high KV motors, high thrust-to-weight margin",
                structural_strategy="IP67 weatherproofing, impact-resistant canopy",
                electrical_strategy="Wide-temperature LiPo battery chemistry"
            )
        elif mission in ["agriculture"]:
            weights = PriorityWeights(
                endurance=0.6, payload_capacity=0.9, efficiency=0.7, agility=0.5,
                wind_resistance=0.6, cost=0.7, reliability=0.8, safety=0.8,
                redundancy=0.6, manufacturability=0.8
            )
            strategy = DesignStrategy(
                key_objective="High-payload spraying and field coverage",
                propulsion_strategy="High torque low KV motors, chemical resistant propellers",
                structural_strategy="Corrosion-resistant materials, integrated spray tank mount",
                electrical_strategy="High capacity quick-swap batteries"
            )
        elif mission in ["indoor inspection"]:
            weights = PriorityWeights(
                endurance=0.5, payload_capacity=0.4, efficiency=0.5, agility=1.0,
                wind_resistance=0.2, cost=0.6, reliability=0.8, safety=0.9,
                redundancy=0.4, manufacturability=0.8
            )
            strategy = DesignStrategy(
                key_objective="Highly agile collision-tolerant indoor flight",
                propulsion_strategy="Shorter high KV motor-propeller combinations for rapid response",
                structural_strategy="Full 360-degree prop guards, compact lightweight frame",
                electrical_strategy="LiPo chemistry for high transient power response"
            )
        elif mission in ["research", "education", "training"]:
            weights = PriorityWeights(
                endurance=0.5, payload_capacity=0.5, efficiency=0.5, agility=0.6,
                wind_resistance=0.5, cost=0.9, reliability=0.7, safety=0.8,
                redundancy=0.3, manufacturability=1.0
            )
            strategy = DesignStrategy(
                key_objective="Low-cost modular open-architecture testbed",
                propulsion_strategy="Commercial off-the-shelf standard parts, nylon props",
                structural_strategy="3D-printed or cheap carbon plate components",
                electrical_strategy="Standard XT60 plug interface, common battery types"
            )
        else:
            # Default / Fallback
            weights = PriorityWeights(
                endurance=0.5, payload_capacity=0.5, efficiency=0.5, agility=0.5,
                wind_resistance=0.5, cost=0.5, reliability=0.5, safety=0.5,
                redundancy=0.5, manufacturability=0.5
            )
            strategy = DesignStrategy(
                key_objective="Multi-mission balanced performance",
                propulsion_strategy="Standard Quadcopter layout with balanced motor/prop matching",
                structural_strategy="Standard carbon fiber plates with tube arms",
                electrical_strategy="Standard LiPo battery configurations"
            )
        return weights, strategy

    def _resolve_recommended_configuration(self, payload: float, redundancy: bool) -> str:
        """
        Determines the recommended multirotor configuration topology based on weight and safety.
        """
        if payload > 15.0:
            return "Coaxial X8"
        
        if redundancy:
            if payload > 8.0:
                return "Octocopter X"
            else:
                return "Hexacopter X"
        else:
            if payload < 1.5:
                return "Quadcopter X"
            elif payload <= 8.0:
                return "Hexacopter X"
            else:
                return "Octocopter X"

    def _resolve_engineering_targets(self, profile: MissionProfile, config: str) -> MissionTargets:
        """
        Derives target parameters like thrust-to-weight, battery classes, and motor KV.
        """
        # 1. Thrust-to-Weight Ratio
        tw = 2.0
        if profile.operating_environment in ["mountain", "marine"] or profile.wind_conditions_kmh > 25.0:
            tw += 0.3
        
        if profile.mission_type in ["cargo delivery", "heavy lift", "delivery"]:
            tw = max(tw, 2.5)

        # 2. Frame Class
        payload = profile.payload_weight_kg
        if payload < 0.5:
            frame_class = "Micro"
            kv_range = (2000.0, 3500.0)
        elif payload <= 1.5:
            frame_class = "Small"
            kv_range = (900.0, 1500.0)
        elif payload <= 5.0:
            frame_class = "Medium"
            kv_range = (600.0, 900.0)
        elif payload <= 15.0:
            frame_class = "Large"
            kv_range = (300.0, 600.0)
        else:
            frame_class = "Heavy Lift"
            kv_range = (100.0, 300.0)

        # 3. Hover Stability
        if profile.mission_type in ["photography", "videography", "inspection", "infrastructure inspection"]:
            stability = "High"
        elif profile.mission_type in ["survey", "mapping", "agriculture", "search & rescue", "emergency response", "security", "surveillance"]:
            stability = "Medium"
        else:
            stability = "Low"

        # 4. Battery Class
        if profile.mission_type in ["survey", "mapping"] or profile.target_flight_time_min > 40.0:
            battery_class = "Li-Ion"
        else:
            battery_class = "LiPo"

        # 5. Propeller Class
        if frame_class in ["Micro", "Small"]:
            propeller_class = "Nylon"
        else:
            propeller_class = "Carbon Fiber"

        # 6. Safety Margin
        safety_margin = 1.2
        if profile.mission_type in ["cargo delivery", "heavy lift", "delivery"]:
            safety_margin = 1.5
        elif profile.mission_type in ["search & rescue", "emergency response"]:
            safety_margin = 1.3

        # 7. Hover/Cruise split
        hover_time = profile.target_flight_time_min
        if profile.mission_type in ["survey", "mapping", "cargo delivery", "delivery"]:
            # Cruise missions spend more time in forward flight
            hover_time = round(profile.target_flight_time_min * 0.3, 1)
            cruise_time = round(profile.target_flight_time_min * 0.7, 1)
        else:
            # Hover missions spend more time in hovering/loitering
            hover_time = round(profile.target_flight_time_min * 0.8, 1)
            cruise_time = round(profile.target_flight_time_min * 0.2, 1)

        return MissionTargets(
            preferred_configuration_class=config,
            preferred_frame_class=frame_class,
            target_thrust_to_weight_ratio=tw,
            target_hover_time_min=hover_time,
            target_cruise_time_min=cruise_time,
            target_hover_stability=stability,
            preferred_battery_class=battery_class,
            preferred_propeller_class=propeller_class,
            preferred_motor_kv_range=kv_range,
            preferred_redundancy=profile.redundancy_required,
            preferred_safety_margin=safety_margin
        )
