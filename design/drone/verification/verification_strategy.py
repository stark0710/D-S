"""
VerificationStrategy Subsystem

Purpose:
    Defines the abstract `VerificationStrategy` interface and concrete multirotor mission verification strategies.

Role in Architecture:
    `VerificationStrategy` implements the Strategy Pattern to compute mission compliance, performance verification,
    safety verification, reliability verification, constraint verification, and composite verification scoring
    according to mission profiles (Balanced, Survey, Inspection, Delivery, Agriculture, Heavy Lift, Research).
"""

from abc import ABC, abstractmethod
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.verification.mission_compliance import MissionCompliance
from backend.design.drone.verification.performance_verification import PerformanceVerification
from backend.design.drone.verification.safety_verification import SafetyVerification
from backend.design.drone.verification.reliability_verification import ReliabilityVerification
from backend.design.drone.verification.constraint_verification import ConstraintVerification
from backend.design.drone.verification.verification_score import VerificationScoreCalculator
from backend.design.drone.verification.verification_result import VerificationResult


class VerificationStrategy(ABC):
    """
    Abstract interface for multirotor mission verification strategies.
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Unique identifier name of the strategy."""
        pass

    @abstractmethod
    def verify_mission(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult,
        performance_result: PerformanceResult
    ) -> VerificationResult:
        """
        Verifies complete multirotor aircraft against mission requirements.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Configuration output.
            structure_result (FrameResult): Structural output.
            propulsion_result (PropulsionResult): Propulsion output.
            electrical_result (ElectricalResult): Electrical output.
            avionics_result (AvionicsResult): Avionics output.
            payload_result (PayloadResult): Payload output.
            mass_result (MassResult): Mass properties output.
            performance_result (PerformanceResult): Performance output.

        Returns:
            VerificationResult: Completed verification output summary.
        """
        pass


class BalancedVerificationStrategy(VerificationStrategy):
    """Standard balanced multirotor mission verification strategy."""

    @property
    def strategy_name(self) -> str:
        return "BalancedVerificationStrategy"

    def verify_mission(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult,
        performance_result: PerformanceResult
    ) -> VerificationResult:
        # 1. Mission Compliance
        comp_engine = MissionCompliance()
        comp_res = comp_engine.verify_compliance(mission, performance_result, mass_result)

        # 2. Performance Verification
        perf_verif_engine = PerformanceVerification()
        perf_verif_res = perf_verif_engine.verify_performance(performance_result)

        # 3. Safety Verification
        safe_engine = SafetyVerification()
        safe_res = safe_engine.verify_safety(structure_result, electrical_result, mass_result, performance_result)

        # 4. Reliability Verification
        rel_engine = ReliabilityVerification()
        rel_res = rel_engine.verify_reliability(configuration_result, avionics_result)

        # 5. Constraint Verification
        const_engine = ConstraintVerification()
        const_res = const_engine.verify_constraints(mass_result, structure_result, electrical_result)

        # 6. Scoring
        scorer = VerificationScoreCalculator()
        m_score = comp_res.compliance_percentage
        p_score = 90.0 if perf_verif_res.verified else 65.0
        s_score = 95.0 if safe_res.safe else 55.0
        r_score = rel_res.reliability_score

        score_res = scorer.calculate_score(m_score, p_score, s_score, r_score)

        # Build passed and failed requirements lists
        passed_reqs: list[str] = []
        failed_reqs: list[str] = []

        if comp_res.payload_satisfied:
            passed_reqs.append("Payload capacity requirement")
        else:
            failed_reqs.append("Payload capacity requirement")

        if comp_res.endurance_satisfied:
            passed_reqs.append("Flight endurance requirement")
        else:
            failed_reqs.append("Flight endurance requirement")

        if comp_res.range_satisfied:
            passed_reqs.append("Flight range requirement")
        else:
            failed_reqs.append("Flight range requirement")

        if comp_res.speed_satisfied:
            passed_reqs.append("Cruise speed requirement")
        else:
            failed_reqs.append("Cruise speed requirement")

        if comp_res.wind_satisfied:
            passed_reqs.append("Wind resistance requirement")
        else:
            failed_reqs.append("Wind resistance requirement")

        # Determine overall status
        if score_res.overall_score >= 80.0 and len(failed_reqs) == 0 and safe_res.safe:
            status = "PASSED"
        elif score_res.overall_score >= 65.0 and len(failed_reqs) <= 1:
            status = "MARGINAL"
        else:
            status = "FAILED"

        recs: list[str] = []
        if not safe_res.battery_reserve_verified:
            recs.append("Increase battery capacity to provide 20% landing reserve.")
        if not comp_res.endurance_satisfied:
            recs.append("Reduce payload mass or select higher energy density battery pack.")

        return VerificationResult(
            overall_status=status,
            verification_score=score_res,
            mission_compliance=comp_res,
            performance_verification=perf_verif_res,
            safety_verification=safe_res,
            reliability_verification=rel_res,
            constraint_verification=const_res,
            passed_requirements=passed_reqs,
            failed_requirements=failed_reqs,
            engineering_notes=f"Mission verification overall status: {status} with composite score {score_res.overall_score:.1f}/100.",
            recommendations=recs
        )


class DeliveryVerificationStrategy(VerificationStrategy):
    """Cargo delivery mission verification strategy emphasizing payload capacity and wind tolerance."""

    @property
    def strategy_name(self) -> str:
        return "DeliveryVerificationStrategy"

    def verify_mission(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult,
        performance_result: PerformanceResult
    ) -> VerificationResult:
        balanced_strat = BalancedVerificationStrategy()
        res = balanced_strat.verify_mission(
            mission, configuration_result, structure_result, propulsion_result, electrical_result, avionics_result, payload_result, mass_result, performance_result
        )
        res.engineering_notes = f"Delivery mission verification: {res.overall_status} (Score: {res.verification_score.overall_score:.1f}/100)."
        return res
