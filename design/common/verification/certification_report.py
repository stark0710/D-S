from typing import List, Dict, Any
from backend.design.common.verification.models import RuleStatus, RuleSeverity
from backend.design.common.verification.verification_result import RuleEvaluationResult

class AircraftCertificationReport:
    def __init__(self, 
                 aircraft_summary: Dict[str, Any], 
                 mission_summary: Dict[str, Any], 
                 results: List[RuleEvaluationResult],
                 feasible: bool = True):
        self.aircraft_summary = aircraft_summary
        self.mission_summary = mission_summary
        self.results = results
        self.feasible = feasible
        
        # Categorize results
        self.passed_rules: List[RuleEvaluationResult] = []
        self.failed_rules: List[RuleEvaluationResult] = []
        self.warnings: List[RuleEvaluationResult] = []
        self.critical_failures: List[RuleEvaluationResult] = []
        
        if not feasible:
            self.overall_status = "NO_FEASIBLE_DESIGN"
            self.certification_score = 0.0
            self.subsystem_compliance = {}
            self.recommendations = ["Optimization engine was unable to synthesize a feasible candidate aircraft configuration."]
            return

        for r in results:
            if r.status == RuleStatus.PASS:
                self.passed_rules.append(r)
            elif r.status == RuleStatus.WARNING:
                self.warnings.append(r)
            elif r.status == RuleStatus.FAIL:
                if r.severity == RuleSeverity.CRITICAL:
                    self.critical_failures.append(r)
                else:
                    self.failed_rules.append(r)

        # Calculate Score
        total_eval = 0
        score_sum = 0.0
        for r in results:
            if r.status == RuleStatus.NOT_APPLICABLE:
                continue
            total_eval += 1
            if r.status == RuleStatus.PASS:
                score_sum += 1.0
            elif r.status == RuleStatus.WARNING:
                score_sum += 0.5
            elif r.status == RuleStatus.FAIL:
                if r.severity == RuleSeverity.WARNING:
                    score_sum += 0.5
                else:
                    score_sum += 0.0

        if total_eval > 0:
            self.certification_score = round((score_sum / total_eval) * 100.0, 1)
        else:
            self.certification_score = 100.0

        # Calculate overall status
        if len(self.critical_failures) > 0 or len(self.failed_rules) > 0:
            self.overall_status = "NOT_CERTIFIED"
        elif len(self.warnings) > 0:
            self.overall_status = "CERTIFIED_WITH_WARNINGS"
        else:
            self.overall_status = "CERTIFIED"

        # Calculate subsystem compliance
        self.subsystem_compliance = self._compute_subsystem_compliance()
        
        # Recommendations
        self.recommendations = self._generate_recommendations()

    def _compute_subsystem_compliance(self) -> Dict[str, str]:
        comp = {}
        category_map = {}
        for r in self.results:
            cat = r.category.value if hasattr(r.category, "value") else str(r.category)
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(r)
            
        for cat, list_res in category_map.items():
            if any(r.status == RuleStatus.FAIL for r in list_res):
                comp[cat] = "Non-Compliant"
            elif any(r.status == RuleStatus.WARNING for r in list_res):
                comp[cat] = "Compliant with Warnings"
            else:
                comp[cat] = "Compliant"
        return comp

    def _generate_recommendations(self) -> List[str]:
        recs = []
        for r in self.critical_failures + self.failed_rules + self.warnings:
            if r.recommendation:
                recs.append(f"[{r.rule_id}] {r.recommendation}")
        if not recs:
            recs.append("No recommendations. Design is fully compliant.")
        return recs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "certification_score": self.certification_score,
            "aircraft_summary": self.aircraft_summary,
            "mission_summary": self.mission_summary,
            "subsystem_compliance": self.subsystem_compliance,
            "passed_rules": [r.to_dict() for r in self.passed_rules],
            "failed_rules": [r.to_dict() for r in self.failed_rules],
            "warnings": [r.to_dict() for r in self.warnings],
            "critical_failures": [r.to_dict() for r in self.critical_failures],
            "recommendations": self.recommendations
        }
