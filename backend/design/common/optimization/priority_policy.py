"""
Optimization Priority Policy Framework

Defines centralized, inspectable, and normalized multi-objective weight configurations
mapped to OptimizationPriority for all subsystem optimizers.
"""

from typing import Dict, Any, Optional
from backend.design.common.requirements.optimization_priority import OptimizationPriority


class OptimizationPriorityPolicy:
    """
    Centralized repository defining how OptimizationPriority maps to 
    objective function weighting across subsystem optimizers.
    """

    # --------------------------------------------------------------------------
    # 1. WingPlanformOptimizer Weights
    # Terms: aerodynamics, structures, mission, stability, manufacturability, packaging
    # --------------------------------------------------------------------------
    WING_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "aerodynamics": 0.30,
            "structures": 0.20,
            "mission": 0.20,
            "stability": 0.15,
            "manufacturability": 0.10,
            "packaging": 0.05,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "structures": 0.35,
            "aerodynamics": 0.25,
            "mission": 0.15,
            "stability": 0.15,
            "manufacturability": 0.05,
            "packaging": 0.05,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "aerodynamics": 0.40,
            "mission": 0.25,
            "structures": 0.15,
            "stability": 0.10,
            "manufacturability": 0.05,
            "packaging": 0.05,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "aerodynamics": 0.45,
            "mission": 0.20,
            "structures": 0.15,
            "stability": 0.10,
            "manufacturability": 0.05,
            "packaging": 0.05,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "aerodynamics": 0.50,
            "structures": 0.15,
            "mission": 0.15,
            "stability": 0.10,
            "manufacturability": 0.05,
            "packaging": 0.05,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "structures": 0.35,
            "aerodynamics": 0.25,
            "mission": 0.15,
            "stability": 0.15,
            "manufacturability": 0.05,
            "packaging": 0.05,
        },
        OptimizationPriority.LOWEST_COST: {
            "manufacturability": 0.35,
            "aerodynamics": 0.20,
            "structures": 0.20,
            "mission": 0.10,
            "stability": 0.10,
            "packaging": 0.05,
        },
    }

    # --------------------------------------------------------------------------
    # 2. FuselageOptimizer Weights
    # Terms: packaging, structures, aerodynamics, manufacturability, cg_margin, mission
    # --------------------------------------------------------------------------
    FUSELAGE_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "packaging": 0.25,
            "structures": 0.20,
            "aerodynamics": 0.20,
            "manufacturability": 0.15,
            "cg_margin": 0.15,
            "mission": 0.05,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "structures": 0.35,
            "packaging": 0.25,
            "aerodynamics": 0.15,
            "cg_margin": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "aerodynamics": 0.30,
            "structures": 0.25,
            "packaging": 0.20,
            "cg_margin": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "aerodynamics": 0.35,
            "structures": 0.20,
            "packaging": 0.20,
            "cg_margin": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "aerodynamics": 0.40,
            "structures": 0.20,
            "packaging": 0.15,
            "cg_margin": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "packaging": 0.40,
            "structures": 0.20,
            "cg_margin": 0.15,
            "aerodynamics": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
        },
        OptimizationPriority.LOWEST_COST: {
            "manufacturability": 0.35,
            "packaging": 0.20,
            "structures": 0.15,
            "aerodynamics": 0.15,
            "cg_margin": 0.10,
            "mission": 0.05,
        },
    }

    # --------------------------------------------------------------------------
    # 3. PayloadPackagingOptimizer Weights
    # Terms: packaging, serviceability, routing, cooling, cg_flexibility
    # --------------------------------------------------------------------------
    PAYLOAD_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "packaging": 0.30,
            "serviceability": 0.20,
            "routing": 0.20,
            "cooling": 0.15,
            "cg_flexibility": 0.15,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "routing": 0.30,
            "packaging": 0.30,
            "cg_flexibility": 0.15,
            "serviceability": 0.15,
            "cooling": 0.10,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "cooling": 0.25,
            "packaging": 0.30,
            "routing": 0.20,
            "serviceability": 0.15,
            "cg_flexibility": 0.10,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "packaging": 0.30,
            "routing": 0.25,
            "cooling": 0.20,
            "serviceability": 0.15,
            "cg_flexibility": 0.10,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "cooling": 0.25,
            "routing": 0.25,
            "packaging": 0.25,
            "serviceability": 0.15,
            "cg_flexibility": 0.10,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "packaging": 0.45,
            "cg_flexibility": 0.25,
            "serviceability": 0.10,
            "cooling": 0.10,
            "routing": 0.10,
        },
        OptimizationPriority.LOWEST_COST: {
            "serviceability": 0.30,
            "routing": 0.25,
            "packaging": 0.25,
            "cooling": 0.10,
            "cg_flexibility": 0.10,
        },
    }

    # --------------------------------------------------------------------------
    # 4. TailOptimizer Weights
    # Terms: longitudinal_stability, directional_stability, low_drag, structural_weight,
    #        manufacturability, mission, cg_robustness
    # --------------------------------------------------------------------------
    TAIL_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "longitudinal_stability": 0.25,
            "directional_stability": 0.15,
            "low_drag": 0.15,
            "structural_weight": 0.10,
            "manufacturability": 0.15,
            "mission": 0.10,
            "cg_robustness": 0.10,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "structural_weight": 0.30,
            "longitudinal_stability": 0.25,
            "directional_stability": 0.15,
            "low_drag": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
            "cg_robustness": 0.05,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "low_drag": 0.30,
            "longitudinal_stability": 0.25,
            "directional_stability": 0.15,
            "structural_weight": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
            "cg_robustness": 0.05,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "low_drag": 0.35,
            "longitudinal_stability": 0.20,
            "directional_stability": 0.15,
            "structural_weight": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
            "cg_robustness": 0.05,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "low_drag": 0.35,
            "structural_weight": 0.15,
            "longitudinal_stability": 0.20,
            "directional_stability": 0.15,
            "manufacturability": 0.05,
            "mission": 0.05,
            "cg_robustness": 0.05,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "longitudinal_stability": 0.30,
            "cg_robustness": 0.20,
            "directional_stability": 0.15,
            "structural_weight": 0.15,
            "low_drag": 0.10,
            "manufacturability": 0.05,
            "mission": 0.05,
        },
        OptimizationPriority.LOWEST_COST: {
            "manufacturability": 0.35,
            "longitudinal_stability": 0.20,
            "directional_stability": 0.15,
            "structural_weight": 0.10,
            "low_drag": 0.10,
            "mission": 0.05,
            "cg_robustness": 0.05,
        },
    }

    # --------------------------------------------------------------------------
    # 5. PropulsionOptimizer Weights
    # Terms: electrical_efficiency, weight, cruise_efficiency, takeoff_margin,
    #        endurance, reliability, future_upgrade_margin
    # --------------------------------------------------------------------------
    PROPULSION_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            # Default baseline matches category-driven weights in PropulsionObjectiveFunction
            "endurance": 0.35,
            "electrical_efficiency": 0.15,
            "weight": 0.10,
            "cruise_efficiency": 0.15,
            "takeoff_margin": 0.05,
            "reliability": 0.10,
            "future_upgrade_margin": 0.10,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "weight": 0.35,
            "cruise_efficiency": 0.20,
            "electrical_efficiency": 0.15,
            "endurance": 0.15,
            "takeoff_margin": 0.05,
            "reliability": 0.05,
            "future_upgrade_margin": 0.05,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "endurance": 0.45,
            "electrical_efficiency": 0.20,
            "cruise_efficiency": 0.15,
            "weight": 0.08,
            "takeoff_margin": 0.04,
            "reliability": 0.04,
            "future_upgrade_margin": 0.04,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "cruise_efficiency": 0.35,
            "electrical_efficiency": 0.25,
            "endurance": 0.20,
            "weight": 0.08,
            "takeoff_margin": 0.04,
            "reliability": 0.04,
            "future_upgrade_margin": 0.04,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "electrical_efficiency": 0.35,
            "cruise_efficiency": 0.30,
            "endurance": 0.15,
            "weight": 0.08,
            "takeoff_margin": 0.04,
            "reliability": 0.04,
            "future_upgrade_margin": 0.04,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "takeoff_margin": 0.35,
            "weight": 0.25,
            "electrical_efficiency": 0.15,
            "endurance": 0.10,
            "cruise_efficiency": 0.05,
            "reliability": 0.05,
            "future_upgrade_margin": 0.05,
        },
        OptimizationPriority.LOWEST_COST: {
            "weight": 0.30,
            "reliability": 0.25,
            "electrical_efficiency": 0.15,
            "endurance": 0.15,
            "cruise_efficiency": 0.10,
            "takeoff_margin": 0.05,
            "future_upgrade_margin": 0.00,
        },
    }

    # --------------------------------------------------------------------------
    # 6. ElectricalOptimizer Weights
    # Terms: reliability, power_margin, weight, cost, manufacturability,
    #        serviceability, mission_compatibility, future_upgrade_margin
    # --------------------------------------------------------------------------
    ELECTRICAL_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "reliability": 0.20,
            "power_margin": 0.15,
            "weight": 0.15,
            "cost": 0.10,
            "manufacturability": 0.10,
            "serviceability": 0.10,
            "mission_compatibility": 0.10,
            "future_upgrade_margin": 0.10,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "weight": 0.35,
            "power_margin": 0.15,
            "reliability": 0.15,
            "future_upgrade_margin": 0.10,
            "cost": 0.10,
            "manufacturability": 0.05,
            "serviceability": 0.05,
            "mission_compatibility": 0.05,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "power_margin": 0.25,
            "reliability": 0.25,
            "weight": 0.15,
            "future_upgrade_margin": 0.15,
            "serviceability": 0.08,
            "mission_compatibility": 0.06,
            "cost": 0.03,
            "manufacturability": 0.03,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "power_margin": 0.25,
            "weight": 0.20,
            "reliability": 0.20,
            "future_upgrade_margin": 0.15,
            "serviceability": 0.08,
            "mission_compatibility": 0.06,
            "cost": 0.03,
            "manufacturability": 0.03,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "power_margin": 0.30,
            "reliability": 0.25,
            "weight": 0.15,
            "future_upgrade_margin": 0.10,
            "mission_compatibility": 0.08,
            "serviceability": 0.06,
            "cost": 0.03,
            "manufacturability": 0.03,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "power_margin": 0.25,
            "reliability": 0.20,
            "weight": 0.20,
            "future_upgrade_margin": 0.15,
            "mission_compatibility": 0.08,
            "serviceability": 0.06,
            "cost": 0.03,
            "manufacturability": 0.03,
        },
        OptimizationPriority.LOWEST_COST: {
            "cost": 0.40,
            "manufacturability": 0.15,
            "weight": 0.15,
            "reliability": 0.10,
            "serviceability": 0.08,
            "power_margin": 0.06,
            "mission_compatibility": 0.03,
            "future_upgrade_margin": 0.03,
        },
    }

    # --------------------------------------------------------------------------
    # 7. MassPropertiesOptimizer Weights
    # Terms: low_empty_weight, payload_fraction, structural_efficiency,
    #        manufacturability, energy_efficiency, growth_margin
    # --------------------------------------------------------------------------
    MASS_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "low_empty_weight": 0.20,
            "payload_fraction": 0.20,
            "structural_efficiency": 0.15,
            "manufacturability": 0.15,
            "energy_efficiency": 0.15,
            "growth_margin": 0.15,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "low_empty_weight": 0.40,
            "structural_efficiency": 0.25,
            "energy_efficiency": 0.15,
            "payload_fraction": 0.10,
            "manufacturability": 0.05,
            "growth_margin": 0.05,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "energy_efficiency": 0.35,
            "low_empty_weight": 0.25,
            "structural_efficiency": 0.15,
            "payload_fraction": 0.10,
            "growth_margin": 0.08,
            "manufacturability": 0.07,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "energy_efficiency": 0.30,
            "structural_efficiency": 0.25,
            "low_empty_weight": 0.20,
            "payload_fraction": 0.10,
            "growth_margin": 0.08,
            "manufacturability": 0.07,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "energy_efficiency": 0.35,
            "structural_efficiency": 0.25,
            "low_empty_weight": 0.15,
            "payload_fraction": 0.10,
            "growth_margin": 0.08,
            "manufacturability": 0.07,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "payload_fraction": 0.45,
            "low_empty_weight": 0.20,
            "structural_efficiency": 0.15,
            "energy_efficiency": 0.10,
            "growth_margin": 0.05,
            "manufacturability": 0.05,
        },
        OptimizationPriority.LOWEST_COST: {
            "manufacturability": 0.40,
            "low_empty_weight": 0.20,
            "structural_efficiency": 0.15,
            "payload_fraction": 0.10,
            "energy_efficiency": 0.10,
            "growth_margin": 0.05,
        },
    }

    # --------------------------------------------------------------------------
    # 8. CGOptimizer Weights
    # Terms: target_stability, packaging_order, mission_suitability,
    #        minimal_movement, payload_flexibility
    # --------------------------------------------------------------------------
    CG_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "target_stability": 0.30,
            "packaging_order": 0.20,
            "mission_suitability": 0.15,
            "minimal_movement": 0.15,
            "payload_flexibility": 0.20,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "target_stability": 0.30,
            "packaging_order": 0.25,
            "minimal_movement": 0.20,
            "mission_suitability": 0.15,
            "payload_flexibility": 0.10,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "target_stability": 0.35,
            "packaging_order": 0.20,
            "mission_suitability": 0.15,
            "minimal_movement": 0.15,
            "payload_flexibility": 0.15,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "target_stability": 0.35,
            "packaging_order": 0.20,
            "mission_suitability": 0.15,
            "minimal_movement": 0.15,
            "payload_flexibility": 0.15,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "target_stability": 0.35,
            "packaging_order": 0.20,
            "mission_suitability": 0.15,
            "minimal_movement": 0.15,
            "payload_flexibility": 0.15,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "payload_flexibility": 0.35,
            "target_stability": 0.25,
            "packaging_order": 0.15,
            "mission_suitability": 0.15,
            "minimal_movement": 0.10,
        },
        OptimizationPriority.LOWEST_COST: {
            "packaging_order": 0.35,
            "minimal_movement": 0.25,
            "target_stability": 0.20,
            "mission_suitability": 0.10,
            "payload_flexibility": 0.10,
        },
    }

    # --------------------------------------------------------------------------
    # 9. FlightPerformanceOptimizer Weights
    # Terms: mission_success, energy_efficiency, safety_margin, operational_perf,
    #        aerodynamic_eff, power_margin
    # --------------------------------------------------------------------------
    FLIGHT_PERFORMANCE_WEIGHTS: Dict[OptimizationPriority, Dict[str, float]] = {
        OptimizationPriority.BALANCED: {
            "mission_success": 0.25,
            "energy_efficiency": 0.20,
            "safety_margin": 0.15,
            "operational_perf": 0.15,
            "aerodynamic_eff": 0.15,
            "power_margin": 0.10,
        },
        OptimizationPriority.LOWEST_WEIGHT: {
            "energy_efficiency": 0.30,
            "mission_success": 0.25,
            "safety_margin": 0.20,
            "aerodynamic_eff": 0.15,
            "power_margin": 0.05,
            "operational_perf": 0.05,
        },
        OptimizationPriority.MAXIMUM_ENDURANCE: {
            "energy_efficiency": 0.35,
            "mission_success": 0.30,
            "aerodynamic_eff": 0.20,
            "safety_margin": 0.05,
            "operational_perf": 0.05,
            "power_margin": 0.05,
        },
        OptimizationPriority.MAXIMUM_RANGE: {
            "aerodynamic_eff": 0.35,
            "energy_efficiency": 0.30,
            "mission_success": 0.20,
            "operational_perf": 0.05,
            "safety_margin": 0.05,
            "power_margin": 0.05,
        },
        OptimizationPriority.HIGHEST_EFFICIENCY: {
            "aerodynamic_eff": 0.35,
            "energy_efficiency": 0.35,
            "mission_success": 0.15,
            "power_margin": 0.05,
            "safety_margin": 0.05,
            "operational_perf": 0.05,
        },
        OptimizationPriority.MAXIMUM_PAYLOAD: {
            "safety_margin": 0.30,
            "mission_success": 0.25,
            "energy_efficiency": 0.20,
            "power_margin": 0.15,
            "aerodynamic_eff": 0.05,
            "operational_perf": 0.05,
        },
        OptimizationPriority.LOWEST_COST: {
            "mission_success": 0.30,
            "safety_margin": 0.20,
            "energy_efficiency": 0.20,
            "aerodynamic_eff": 0.15,
            "power_margin": 0.10,
            "operational_perf": 0.05,
        },
    }

    # --------------------------------------------------------------------------
    # Accessor Helpers
    # --------------------------------------------------------------------------
    @classmethod
    def get_wing_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.WING_WEIGHTS.get(priority, cls.WING_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_fuselage_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.FUSELAGE_WEIGHTS.get(priority, cls.FUSELAGE_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_payload_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.PAYLOAD_WEIGHTS.get(priority, cls.PAYLOAD_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_tail_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.TAIL_WEIGHTS.get(priority, cls.TAIL_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_propulsion_weights(
        cls,
        priority: OptimizationPriority,
        mission_category_name: Optional[str] = None
    ) -> Dict[str, float]:
        if priority == OptimizationPriority.BALANCED:
            # Baseline behavior preserves the existing mission category adjustments
            weights = {
                "electrical_efficiency": 0.15,
                "weight": 0.15,
                "cruise_efficiency": 0.15,
                "takeoff_margin": 0.15,
                "endurance": 0.20,
                "reliability": 0.10,
                "future_upgrade_margin": 0.10,
            }
            if mission_category_name:
                cat_name = mission_category_name
                if any(w in cat_name for w in ["Endurance", "Survey", "Mapping", "Agriculture"]):
                    weights["endurance"] = 0.35
                    weights["electrical_efficiency"] = 0.15
                    weights["weight"] = 0.10
                    weights["cruise_efficiency"] = 0.15
                    weights["takeoff_margin"] = 0.05
                elif "Cargo" in cat_name:
                    weights["takeoff_margin"] = 0.35
                    weights["weight"] = 0.15
                    weights["reliability"] = 0.15
                    weights["endurance"] = 0.10
                elif "Racing" in cat_name:
                    weights["takeoff_margin"] = 0.30
                    weights["weight"] = 0.20
                    weights["electrical_efficiency"] = 0.05
                    weights["endurance"] = 0.05
            return cls._normalize_weights(weights)

        # For non-BALANCED priorities, retrieve priority-specific weight configuration
        weights = cls.PROPULSION_WEIGHTS.get(priority, cls.PROPULSION_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_electrical_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.ELECTRICAL_WEIGHTS.get(priority, cls.ELECTRICAL_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_mass_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.MASS_WEIGHTS.get(priority, cls.MASS_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_cg_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.CG_WEIGHTS.get(priority, cls.CG_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @classmethod
    def get_flight_performance_weights(cls, priority: OptimizationPriority) -> Dict[str, float]:
        weights = cls.FLIGHT_PERFORMANCE_WEIGHTS.get(priority, cls.FLIGHT_PERFORMANCE_WEIGHTS[OptimizationPriority.BALANCED])
        return cls._normalize_weights(weights)

    @staticmethod
    def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
        total = sum(weights.values())
        if total <= 0.0:
            return weights.copy()
        return {k: v / total for k, v in weights.items()}
