import unittest
from unittest.mock import MagicMock
from backend.design.common.verification.models import RuleSeverity, RuleCategory, RuleStatus, VerificationRule
from backend.design.common.verification.rule_registry import RuleRegistry, global_registry
from backend.design.common.verification.rule_loader import RuleLoader
from backend.design.common.verification.rule_engine import RuleEngine
from backend.design.common.verification.verification_context import VerificationContext
from backend.design.common.verification.certification_report import AircraftCertificationReport
from backend.design.common.verification.verification_engine import VerificationEngine

class DummyRule(VerificationRule):
    def __init__(self, rule_id, status=RuleStatus.PASS, severity=RuleSeverity.ERROR):
        super().__init__(
            rule_id=rule_id,
            title="Dummy Rule",
            description="A dummy test rule",
            category=RuleCategory.SAFETY,
            severity=severity
        )
        self.status = status
        self.config_type = "Conventional"

    def evaluate(self, context):
        if self.status == RuleStatus.PASS:
            return RuleStatus.PASS, "Passed", ""
        elif self.status == RuleStatus.WARNING:
            return RuleStatus.WARNING, "Warning occurred", "Do caution check"
        else:
            return RuleStatus.FAIL, "Failure occurred", "Please fix it"

class TestVerificationEngine(unittest.TestCase):
    def test_rule_registry(self):
        registry = RuleRegistry()
        rule1 = DummyRule("T1")
        rule2 = DummyRule("T2")
        registry.register_rule("Conventional", rule1)
        registry.register_rule("Multirotor", rule2)

        conv_rules = registry.get_rules("Conventional")
        self.assertEqual(len(conv_rules), 1)
        self.assertEqual(conv_rules[0].rule_id, "T1")

        mr_rules = registry.get_rules("Multirotor")
        self.assertEqual(len(mr_rules), 1)
        self.assertEqual(mr_rules[0].rule_id, "T2")

    def test_rule_engine(self):
        engine = RuleEngine()
        context = VerificationContext(None, None, {})
        rules = [
            DummyRule("T1", RuleStatus.PASS),
            DummyRule("T2", RuleStatus.FAIL, RuleSeverity.CRITICAL),
            DummyRule("T3", RuleStatus.WARNING)
        ]
        results = engine.execute_rules(context, rules)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].status, RuleStatus.PASS)
        self.assertEqual(results[1].status, RuleStatus.FAIL)
        self.assertEqual(results[2].status, RuleStatus.WARNING)

    def test_certification_report(self):
        # 100% compliant
        results1 = [
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R1", recommendation=""),
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.CRITICAL, category=RuleCategory.WING, rule_id="R2", recommendation="")
        ]
        report1 = AircraftCertificationReport({}, {}, results1)
        self.assertEqual(report1.overall_status, "CERTIFIED")
        self.assertEqual(report1.certification_score, 100.0)

        # Warning compliant
        results2 = [
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R1", recommendation=""),
            MagicMock(status=RuleStatus.WARNING, severity=RuleSeverity.WARNING, category=RuleCategory.WING, rule_id="R2", recommendation="Be careful")
        ]
        report2 = AircraftCertificationReport({}, {}, results2)
        self.assertEqual(report2.overall_status, "CERTIFIED_WITH_WARNINGS")
        self.assertEqual(report2.certification_score, 75.0)

        # Non-compliant due to ERROR fail
        results3 = [
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R1", recommendation=""),
            MagicMock(status=RuleStatus.FAIL, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R2", recommendation="Fix wing thickness")
        ]
        report3 = AircraftCertificationReport({}, {}, results3)
        self.assertEqual(report3.overall_status, "NOT_CERTIFIED")
        self.assertEqual(report3.certification_score, 50.0)

        # Infeasible design
        report4 = AircraftCertificationReport({}, {}, [], feasible=False)
        self.assertEqual(report4.overall_status, "NO_FEASIBLE_DESIGN")
        self.assertEqual(report4.certification_score, 0.0)

    def test_rule_loader(self):
        """Test that rule loader discovers and instantiates all rules from the rules directory."""
        import os
        rules_dir = os.path.join(os.path.dirname(__file__), "..", "rules")
        loaded = RuleLoader.load_rules_from_directory(rules_dir)
        # We have at least 11 rule files
        self.assertGreaterEqual(len(loaded), 10)
        # Each loaded rule should be a VerificationRule subclass
        for rule in loaded:
            self.assertIsInstance(rule, VerificationRule)
            self.assertTrue(len(rule.rule_id) > 0)
            self.assertTrue(len(rule.title) > 0)

    def test_severity_ordering(self):
        """Test that CRITICAL failures dominate over ERROR failures in status."""
        results = [
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.INFO, category=RuleCategory.MISSION, rule_id="R1", recommendation=""),
            MagicMock(status=RuleStatus.FAIL, severity=RuleSeverity.CRITICAL, category=RuleCategory.PROPULSION, rule_id="R2", recommendation="Fix motor"),
            MagicMock(status=RuleStatus.FAIL, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R3", recommendation="Fix wing"),
        ]
        report = AircraftCertificationReport({}, {}, results)
        self.assertEqual(report.overall_status, "NOT_CERTIFIED")
        self.assertEqual(len(report.critical_failures), 1)
        self.assertEqual(len(report.failed_rules), 1)

    def test_report_to_dict(self):
        """Test that the certification report serializes to a dictionary."""
        results = [
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R1", recommendation="",
                      to_dict=lambda: {"rule_id": "R1", "status": "PASS"}),
        ]
        report = AircraftCertificationReport({"layout": "Conventional"}, {"category": "Survey"}, results)
        d = report.to_dict()
        self.assertIn("overall_status", d)
        self.assertIn("certification_score", d)
        self.assertIn("aircraft_summary", d)
        self.assertIn("mission_summary", d)
        self.assertIn("subsystem_compliance", d)
        self.assertIn("recommendations", d)
        self.assertEqual(d["overall_status"], "CERTIFIED")

    def test_rule_engine_exception_handling(self):
        """Test that rules which throw exceptions are caught and recorded as FAIL."""
        class CrashingRule(VerificationRule):
            def __init__(self):
                super().__init__(
                    rule_id="CRASH",
                    title="Crasher",
                    description="Always crashes",
                    category=RuleCategory.SAFETY,
                    severity=RuleSeverity.CRITICAL
                )
            def evaluate(self, context):
                raise ValueError("Intentional test error")

        engine = RuleEngine()
        context = VerificationContext(None, None, {})
        results = engine.execute_rules(context, [CrashingRule()])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, RuleStatus.FAIL)
        self.assertIn("exception", results[0].message)

    def test_not_applicable_excluded_from_score(self):
        """Test that NOT_APPLICABLE rules do not impact the certification score."""
        results = [
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R1", recommendation=""),
            MagicMock(status=RuleStatus.NOT_APPLICABLE, severity=RuleSeverity.INFO, category=RuleCategory.ELECTRICAL, rule_id="R2", recommendation=""),
        ]
        report = AircraftCertificationReport({}, {}, results)
        self.assertEqual(report.overall_status, "CERTIFIED")
        self.assertEqual(report.certification_score, 100.0)

    def test_subsystem_compliance_map(self):
        """Test that subsystem compliance categorizes correctly."""
        results = [
            MagicMock(status=RuleStatus.PASS, severity=RuleSeverity.ERROR, category=RuleCategory.WING, rule_id="R1", recommendation=""),
            MagicMock(status=RuleStatus.FAIL, severity=RuleSeverity.ERROR, category=RuleCategory.PROPULSION, rule_id="R2", recommendation="Fix"),
            MagicMock(status=RuleStatus.WARNING, severity=RuleSeverity.WARNING, category=RuleCategory.MASS, rule_id="R3", recommendation="Check"),
        ]
        report = AircraftCertificationReport({}, {}, results)
        self.assertEqual(report.subsystem_compliance["Wing"], "Compliant")
        self.assertEqual(report.subsystem_compliance["Propulsion"], "Non-Compliant")
        self.assertEqual(report.subsystem_compliance["Mass"], "Compliant with Warnings")
