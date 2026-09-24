"""
Unit tests for Universal Engineering Design Report Framework.
"""

import pytest
import json
from backend.design.common.requirements import MissionType, RequirementModel
from backend.design.common.context import ContextBuilder
from backend.design.studio.artifacts import ArtifactCategory, ArtifactFactory
from backend.design.studio.reports import (
    ReportSection,
    EngineeringReport,
    DroneReportTemplate,
    FixedWingReportTemplate,
    VTOLReportTemplate,
    ReportBuilder,
    ReportValidator,
    ReportValidationError,
    JSONReportExporter,
    MarkdownReportExporter,
    HTMLReportExporter,
    ReportRegistry,
    ReportPipeline,
    ReportGenerator,
)


def test_report_builder_and_templates():
    """Verify ReportBuilder builds report using layout template."""
    art_factory = ArtifactFactory()
    a1 = art_factory.create_artifact("Mission Spec", ArtifactCategory.MISSION, {"type": "AGRICULTURE"})
    a2 = art_factory.create_artifact("Motor Spec", ArtifactCategory.MOTOR_SELECTION, {"kv": 300})
    a3 = art_factory.create_artifact("Perf Analysis", ArtifactCategory.PERFORMANCE_ANALYSIS, {"endurance": 45})

    builder = ReportBuilder()
    builder.set_title("Hexacopter Design Report")
    builder.set_summary("Comprehensive engineering design report.")
    builder.add_artifacts([a1, a2, a3])
    builder.apply_template(DroneReportTemplate())

    report = builder.build()

    assert isinstance(report, EngineeringReport)
    assert report.title == "Hexacopter Design Report"
    assert len(report.sections) >= 4
    assert report.sections[0].title == "1. Executive Summary"


def test_report_validator():
    """Verify ReportValidator validates report structure and section ordering."""
    validator = ReportValidator()

    sec1 = ReportSection(title="1. Summary", order=1, content="Content 1")
    sec2 = ReportSection(title="2. Details", order=2, content="Content 2")
    report_ok = EngineeringReport(report_id="REP-001", title="Valid Report", sections=[sec1, sec2])

    assert validator.validate(report_ok)

    report_invalid_id = EngineeringReport(report_id="", title="No ID", sections=[sec1])
    with pytest.raises(ReportValidationError):
        validator.validate(report_invalid_id)

    report_no_sections = EngineeringReport(report_id="REP-002", title="Empty Sections", sections=[])
    with pytest.raises(ReportValidationError):
        validator.validate(report_no_sections)


def test_report_exporters():
    """Verify JSON, Markdown, and HTML report exporters."""
    sec = ReportSection(title="1. Introduction", order=1, content="This is test content.")
    report = EngineeringReport(report_id="REP-100", title="Test Export Report", sections=[sec])

    json_exp = JSONReportExporter()
    json_out = json_exp.export(report)
    assert json.loads(json_out)["title"] == "Test Export Report"

    md_exp = MarkdownReportExporter()
    md_out = md_exp.export(report)
    assert "# Test Export Report" in md_out
    assert "## 1. Introduction" in md_out

    html_exp = HTMLReportExporter()
    html_out = html_exp.export(report)
    assert "<h1>Test Export Report</h1>" in html_out


def test_report_generator_execution():
    """Verify ReportGenerator generates report and formatted document string."""
    req = RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=3.0,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=60.0
    )
    context = ContextBuilder.create_context(req)

    art_factory = ArtifactFactory()
    artifacts = [
        art_factory.create_artifact("Mission Requirement", ArtifactCategory.MISSION, {"payload": 3.0}),
        art_factory.create_artifact("Propulsion Sizing", ArtifactCategory.MOTOR_SELECTION, {"motor": "MN501S"}),
    ]

    generator = ReportGenerator()
    report, md_str = generator.generate_report(
        context=context,
        artifacts=artifacts,
        template_name="DroneReportTemplate",
        title="Delivery Quadcopter Engineering Report",
        export_format="MARKDOWN"
    )

    assert isinstance(report, EngineeringReport)
    assert "Delivery Quadcopter Engineering Report" in md_str
    assert "Executive Summary" in md_str
