"""
Fixed-Wing Mission Verification Sizing Engine Subsystem

Purpose:
    Defines the `VerificationEngine` class, which serves as the orchestrator for the Sizing Verification Framework.

Role in Architecture:
    `VerificationEngine` coordinates compliance reports, risk analyses, and checkers,
    running validation loops.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime

from backend.design.fixed_wing.verification.verification_requirements import VerificationRequirements
from backend.design.fixed_wing.verification.verification_profile import VerificationProfile
from backend.design.fixed_wing.verification.verification_constraints import VerificationConstraints
from backend.design.fixed_wing.verification.verification_result import VerificationResult
from backend.design.fixed_wing.verification.verification_validator import VerificationValidator
from backend.design.fixed_wing.verification.verification_registry import VerificationStrategyRegistry
from backend.design.fixed_wing.verification.requirement_checker import RequirementChecker
from backend.design.fixed_wing.verification.mission_checker import MissionChecker
from backend.design.fixed_wing.verification.performance_checker import PerformanceChecker
from backend.design.fixed_wing.verification.stability_checker import StabilityChecker
from backend.design.fixed_wing.verification.safety_checker import SafetyChecker
from backend.design.fixed_wing.verification.component_checker import ComponentChecker
from backend.design.fixed_wing.verification.constraint_checker import ConstraintChecker
from backend.design.fixed_wing.verification.risk_analysis import RiskAnalysis
from backend.design.fixed_wing.verification.compliance_report import ComplianceReport


class VerificationEngine:
    """
    Orchestrator driving the fixed-wing design verification and compliance audits.
    """

    def __init__(
        self,
        validator: VerificationValidator | None = None,
        req_checker: RequirementChecker | None = None,
        mission_checker: MissionChecker | None = None,
        perf_checker: PerformanceChecker | None = None,
        stab_checker: StabilityChecker | None = None,
        safety_checker: SafetyChecker | None = None,
        comp_checker: ComponentChecker | None = None,
        const_checker: ConstraintChecker | None = None,
    ) -> None:
        self._validator = validator if validator else VerificationValidator()
        self._req_checker = req_checker if req_checker else RequirementChecker()
        self._mission_checker = mission_checker if mission_checker else MissionChecker()
        self._perf_checker = perf_checker if perf_checker else PerformanceChecker()
        self._stab_checker = stab_checker if stab_checker else StabilityChecker()
        self._safety_checker = safety_checker if safety_checker else SafetyChecker()
        self._comp_checker = comp_checker if comp_checker else ComponentChecker()
        self._const_checker = const_checker if const_checker else ConstraintChecker()

    def process_verification(
        self,
        requirements: VerificationRequirements,
        profile: VerificationProfile | None = None,
    ) -> VerificationResult:
        """
        Runs complete checks and compiles a VerificationResult.

        Args:
            requirements (VerificationRequirements): Sizing requirements context.
            profile (VerificationProfile | None): references and score limits.

        Returns:
            VerificationResult: checklist evaluations, risk levels, and compliance logs.
        """
        if profile is None:
            profile = VerificationProfile()

        # Check for missing mandatory sub-results at the very beginning
        mandatory_fields = [
            "mission_result", "configuration_result", "wing_result", 
            "airfoil_result", "tail_result", "fuselage_result", 
            "propulsion_result", "avionics_result", "payload_result", 
            "mass_result", "flight_result"
        ]
        missing_fields = []
        if requirements is None:
            missing_fields.append("requirements")
        else:
            for field_name in mandatory_fields:
                if getattr(requirements, field_name, None) is None:
                    missing_fields.append(field_name)

        if missing_fields:
            verified_cats: List[str] = []
            failed_cats = ["Missing Data"]
            comp_details = {"Missing Data": f"Deficient: Missing mandatory result: {'; '.join(missing_fields)}"}
            
            report = ComplianceReport(
                compliance_score_pct=0.0,
                is_fully_compliant=False,
                verified_categories=verified_cats,
                failed_categories=failed_cats,
                compliance_details=comp_details,
            )
            
            risk = RiskAnalysis(
                overall_risk_score=100.0,
                risk_level="High",
                identified_risks=[f"Missing mandatory result: {f}" for f in missing_fields],
                mitigation_actions=["Sizing loop failed to produce complete design results. Rerun design pipeline."],
            )
            
            metadata = {
                "engine_version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            return VerificationResult(
                mission_status="Deficient",
                verification_status="FAILED",
                requirement_results={"Missing Data": False},
                compliance_report=report,
                risk_analysis=risk,
                constraint_violations=[f"Missing mandatory result: {f}" for f in missing_fields],
                engineering_notes=["Requirements object or sub-stage outputs are missing."],
                recommendations=["Rerun sizing pipeline to resolve missing sub-stage outputs."],
                corrective_actions=["Sizing loop failed to produce complete design results. Rerun design pipeline."],
                warnings=[],
                metadata=metadata,
            )

        m_profile = requirements.mission_result.mission_profile
        category = m_profile.mission_category

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = VerificationStrategyRegistry.get(strategy_name)

        # target margins
        min_comp, max_risk = strategy.get_passing_bounds()

        # Define constraints
        constraints = VerificationConstraints(
            min_compliance_pct=min_comp,
            max_acceptable_risk_rating="High" if max_risk > 40.0 else "Medium",
            max_allowed_violations=3,
        )

        violations: List[str] = []
        warnings: List[str] = []

        if missing_fields:
            for f in missing_fields:
                violations.append(f"Missing mandatory result: {f}")
            req_failures = []
            mission_failures = []
            perf_failures = []
            stab_failures = []
            safety_failures = []
            comp_failures = []
            const_failures = []
        else:
            # 2. Run checkers
            req_failures = self._req_checker.check_requirements(requirements)
            mission_failures = self._mission_checker.check_mission_suitability(requirements)
            perf_failures = self._perf_checker.check_performance_suitability(requirements)
            stab_failures = self._stab_checker.check_stability_suitability(requirements)
            safety_failures = self._safety_checker.check_safety_suitability(requirements)
            comp_failures = self._comp_checker.check_subsystem_compatibility(requirements)
            const_failures = self._const_checker.check_constraints(requirements)

            violations.extend(mission_failures)
            violations.extend(perf_failures)
            violations.extend(stab_failures)
            violations.extend(comp_failures)
            violations.extend(const_failures)
            violations.extend(safety_failures) # Safety failures are violations (HARD FAIL)!

            warnings.extend(req_failures)

        # 4. Sizing Compliance Score
        compliance_pct = 100.0 - (len(violations) * 12.0) - (len(warnings) * 4.0)
        compliance_pct = max(0.0, min(100.0, compliance_pct))
        is_compliant = (len(violations) == 0) and (not missing_fields)

        # Sizing verified vs failed categories
        verified_cats: List[str] = []
        failed_cats: List[str] = []
        comp_details: Dict[str, str] = {}

        categories = {
            "Mission": mission_failures,
            "Performance": perf_failures,
            "Stability": stab_failures,
            "Safety": safety_failures,
            "Component Clearance": comp_failures,
            "Structural Constraints": const_failures,
        }

        for cat, fails in categories.items():
            if fails:
                failed_cats.append(cat)
                comp_details[cat] = f"Deficient: {'; '.join(fails)}"
            else:
                verified_cats.append(cat)
                comp_details[cat] = "Compliant"

        report = ComplianceReport(
            compliance_score_pct=round(compliance_pct, 1),
            is_fully_compliant=is_compliant,
            verified_categories=verified_cats,
            failed_categories=failed_cats,
            compliance_details=comp_details,
        )

        # 5. Sizing Risk Assessment
        risk_score = (len(violations) * 15.0) + (len(warnings) * 5.0)
        risk_score = max(0.0, min(100.0, risk_score))
        
        if risk_score <= 15.0:
            risk_lvl = "Low"
        elif risk_score <= 35.0:
            risk_lvl = "Medium"
        else:
            risk_lvl = "High"

        identified_risks: List[str] = []
        identified_risks.extend(violations)
        identified_risks.extend(warnings)

        mitigations = strategy.get_remedial_actions()

        risk = RiskAnalysis(
            overall_risk_score=round(risk_score, 1),
            risk_level=risk_lvl,
            identified_risks=identified_risks,
            mitigation_actions=mitigations,
        )

        # 6. Sizing check status
        if not is_compliant or missing_fields:
            v_status = "FAILED"
        elif len(warnings) > 0:
            v_status = "VERIFIED_WITH_WARNINGS"
        else:
            v_status = "VERIFIED"
        m_status = "Ready" if (is_compliant and risk_lvl != "High") else "Deficient"

        # 7. Sizing validation checks
        validation_warnings = self._validator.validate(
            compliance_pct=compliance_pct,
            min_compliance_pct=0.0 if len(violations) == 0 else min_comp,
            risk_score=risk_score,
            max_risk_score=max_risk,
            violations=violations,
        )

        # 8. Sizing recommendations
        recs = [
            f"Verification status: {v_status}, overall compliance: {compliance_pct:.1f}%.",
            f"Risk index: {risk_score:.1f} ({risk_lvl} Risk level).",
            f"Verified {len(verified_cats)} subsystem categories, flagged {len(failed_cats)} deficiencies.",
        ]

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
        }

        # 9. Return VerificationResult
        return VerificationResult(
            mission_status=m_status,
            verification_status=v_status,
            requirement_results={cat: not bool(fails) for cat, fails in categories.items()},
            compliance_report=report,
            risk_analysis=risk,
            constraint_violations=violations,
            engineering_notes=[
                f"Mission category: {category.value}.",
                f"Sized compliance score: {compliance_pct:.1f}%.",
            ],
            recommendations=recs,
            corrective_actions=mitigations if not is_compliant else [],
            warnings=warnings + validation_warnings,
            metadata=metadata,
        )
