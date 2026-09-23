from typing import List
from backend.design.common.verification.models import VerificationRule, RuleStatus
from backend.design.common.verification.verification_context import VerificationContext
from backend.design.common.verification.verification_result import RuleEvaluationResult

class RuleEngine:
    def execute_rules(self, context: VerificationContext, rules: List[VerificationRule]) -> List[RuleEvaluationResult]:
        results = []
        for rule in rules:
            try:
                status, msg, rec = rule.evaluate(context)
                res = RuleEvaluationResult(
                    rule_id=rule.rule_id,
                    title=rule.title,
                    category=rule.category,
                    severity=rule.severity,
                    status=status,
                    message=msg,
                    recommendation=rec
                )
                results.append(res)
            except Exception as e:
                res = RuleEvaluationResult(
                    rule_id=rule.rule_id,
                    title=rule.title,
                    category=rule.category,
                    severity=rule.severity,
                    status=RuleStatus.FAIL,
                    message=f"Rule execution threw an exception: {e}",
                    recommendation="Review rule implementation for safety."
                )
                results.append(res)
        return results
