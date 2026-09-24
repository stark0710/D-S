"""
ConfigurationEngine Subsystem

Purpose:
    Defines the `ConfigurationEngine` class, which serves as the public entry point for multirotor configuration engineering evaluation.

Role in Architecture:
    `ConfigurationEngine` receives a `DroneMissionProfile`, resolves ranking strategy from `ConfigurationRegistry`,
    evaluates standard multirotor frame architectures (Quad X, Quad +, Hexacopter, Y6, Octocopter, X8),
    validates candidates against constraints, and returns a `ConfigurationResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_profile import ConfigurationProfile
from backend.design.drone.configuration.configuration_candidate import ConfigurationCandidate
from backend.design.drone.configuration.configuration_constraints import ConfigurationConstraints
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.configuration.configuration_validator import ConfigurationValidator
from backend.design.drone.configuration.configuration_registry import ConfigurationRegistry
from backend.design.drone.configuration.configuration_strategy import (
    BalancedStrategy,
    LowestCostConfigurationStrategy,
    MaximumPayloadStrategy,
    MaximumReliabilityStrategy,
    LongEnduranceStrategy,
    HeavyLiftStrategy,
)


def _get_standard_profiles() -> list[ConfigurationProfile]:
    """Returns standard multirotor frame configuration profiles."""
    return [
        ConfigurationProfile(
            config_type="QUAD_X",
            rotor_count=4,
            coaxial=False,
            description="Quadrotor in X layout. High efficiency, simple control, low BOM cost.",
            advantages=["Lowest BOM component count", "High hover efficiency", "Simple maintenance"],
            disadvantages=["Zero motor loss redundancy", "Limited maximum payload capacity"]
        ),
        ConfigurationProfile(
            config_type="QUAD_PLUS",
            rotor_count=4,
            coaxial=False,
            description="Quadrotor in + layout. Intuitive pitch/roll control.",
            advantages=["Simple control axis alignment", "Low BOM cost"],
            disadvantages=["Zero motor loss redundancy", "Propellers in forward camera FOV"]
        ),
        ConfigurationProfile(
            config_type="HEXACOPTER",
            rotor_count=6,
            coaxial=False,
            description="Hexacopter in 6-rotor radial layout. Single motor failure redundancy.",
            advantages=["Single motor loss emergency recovery", "Higher total thrust capacity"],
            disadvantages=["Larger frame footprint", "2 additional motors/ESCs cost"]
        ),
        ConfigurationProfile(
            config_type="Y6",
            rotor_count=6,
            coaxial=True,
            description="Y-frame coaxial hexacopter with 3 arms and 6 rotors.",
            advantages=["Compact frame footprint", "Single motor loss redundancy"],
            disadvantages=["~12-15% lower rotor efficiency due to coaxial inflow loss"]
        ),
        ConfigurationProfile(
            config_type="OCTOCOPTER",
            rotor_count=8,
            coaxial=False,
            description="Octocopter in 8-rotor radial layout. Dual motor failure redundancy.",
            advantages=["Dual motor loss emergency recovery", "High payload capacity", "Redundant control authority"],
            disadvantages=["High BOM cost (8 motors/ESCs)", "Large frame footprint"]
        ),
        ConfigurationProfile(
            config_type="X8",
            rotor_count=8,
            coaxial=True,
            description="X-frame coaxial octocopter with 4 arms and 8 rotors.",
            advantages=["Compact footprint", "High payload capacity", "Dual motor loss redundancy"],
            disadvantages=["Coaxial aerodynamic efficiency loss (~15%)"]
        ),
    ]


class ConfigurationEngine:
    """
    Public entry point service for multirotor frame configuration engineering.

    Design Principles:
        - Single Responsibility Principle: Multirotor frame architecture evaluation only.
        - Dependency Injection: Injects `ConfigurationRegistry` and `ConfigurationValidator` collaborators.
        - Non-Calculation: Performs no component selection or trade-off optimization.
    """

    def __init__(
        self,
        registry: ConfigurationRegistry | None = None,
        validator: ConfigurationValidator | None = None
    ) -> None:
        """
        Initializes the ConfigurationEngine.

        Args:
            registry (ConfigurationRegistry | None): Injected strategy registry.
            validator (ConfigurationValidator | None): Injected candidate validator.
        """
        if registry is None:
            registry = ConfigurationRegistry()
            registry.register_strategy(BalancedStrategy())
            registry.register_strategy(LowestCostConfigurationStrategy())
            registry.register_strategy(MaximumPayloadStrategy())
            registry.register_strategy(MaximumReliabilityStrategy())
            registry.register_strategy(LongEnduranceStrategy())
            registry.register_strategy(HeavyLiftStrategy())

        self._registry: ConfigurationRegistry = registry
        self._validator: ConfigurationValidator = validator if validator else ConfigurationValidator()

    def evaluate_configurations(
        self,
        mission: DroneMissionProfile,
        strategy_name: str = "BalancedStrategy",
        constraints: ConfigurationConstraints | None = None
    ) -> ConfigurationResult:
        """
        Evaluates and ranks multirotor frame configurations for the given mission.

        Args:
            mission (DroneMissionProfile): Target multirotor mission profile.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (ConfigurationConstraints | None): Frame configuration constraints.

        Returns:
            ConfigurationResult: Ranked multirotor configuration output.
        """
        const = constraints if constraints else ConfigurationConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        # 1. Build candidates
        profiles = _get_standard_profiles()
        candidates = [ConfigurationCandidate(profile=p) for p in profiles]

        # 2. Score & Rank candidates
        ranked_candidates = strategy.rank_candidates(candidates, mission)

        # 3. Validate candidates against constraints
        all_warnings: list[str] = []
        for c in ranked_candidates:
            c_warns = self._validator.validate_candidate(c, const)
            if c_warns:
                all_warnings.extend(c_warns)

        recommended = ranked_candidates[0]
        justification = (
            f"Recommended '{recommended.profile.config_type}' configuration ({recommended.profile.description}) "
            f"using {strategy_name}. Rated top choice with suitability score {recommended.suitability_score:.2f}."
        )

        tradeoffs = list(recommended.profile.disadvantages)

        return ConfigurationResult(
            recommended_configuration=recommended,
            candidate_configurations=ranked_candidates,
            engineering_justification=justification,
            tradeoffs=tradeoffs,
            warnings=all_warnings,
            metadata={"strategy": strategy_name}
        )
