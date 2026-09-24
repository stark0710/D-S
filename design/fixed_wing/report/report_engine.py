"""
Fixed-Wing Engineering Report Engine Subsystem

Purpose:
    Defines the `ReportEngine` class, which serves as the orchestrator for the Engineering Report Framework.

Role in Architecture:
    `ReportEngine` coordinates section compilers, renders the unified document body,
    exports to multiple file formats, and validates report completeness.
"""

from typing import Dict, Any
from datetime import datetime
import json
import os

from backend.design.fixed_wing.report.report_requirements import ReportRequirements
from backend.design.fixed_wing.report.report_profile import ReportProfile
from backend.design.fixed_wing.report.report_constraints import ReportConstraints
from backend.design.fixed_wing.report.report_result import ReportResult
from backend.design.fixed_wing.report.report_validator import ReportValidator
from backend.design.fixed_wing.report.report_registry import ReportStrategyRegistry
from backend.design.fixed_wing.report.report_renderer import ReportRenderer
from backend.design.fixed_wing.report.pdf_export import PDFExport
from backend.design.fixed_wing.report.html_export import HTMLExport
from backend.design.fixed_wing.report.markdown_export import MarkdownExport
from backend.design.fixed_wing.report.executive_summary import ExecutiveSummaryCompiler
from backend.design.fixed_wing.report.mission_section import MissionSectionCompiler
from backend.design.fixed_wing.report.configuration_section import ConfigurationSectionCompiler
from backend.design.fixed_wing.report.geometry_section import GeometrySectionCompiler
from backend.design.fixed_wing.report.propulsion_section import PropulsionSectionCompiler
from backend.design.fixed_wing.report.electrical_section import ElectricalSectionCompiler
from backend.design.fixed_wing.report.avionics_section import AvionicsSectionCompiler
from backend.design.fixed_wing.report.payload_section import PayloadSectionCompiler
from backend.design.fixed_wing.report.mass_properties_section import MassPropertiesSectionCompiler
from backend.design.fixed_wing.report.flight_performance_section import FlightPerformanceSectionCompiler
from backend.design.fixed_wing.report.verification_section import VerificationSectionCompiler
from backend.design.fixed_wing.report.optimization_section import OptimizationSectionCompiler
from backend.design.fixed_wing.report.cad_section import CADSectionCompiler
from backend.design.fixed_wing.report.manufacturing_section import ManufacturingSectionCompiler
from backend.design.fixed_wing.report.appendix_section import AppendixSectionCompiler


class ReportEngine:
    """
    Orchestrator driving the fixed-wing engineering report compilation workflow.
    """

    def __init__(
        self,
        validator: ReportValidator | None = None,
        renderer: ReportRenderer | None = None,
        pdf_export: PDFExport | None = None,
        html_export: HTMLExport | None = None,
        md_export: MarkdownExport | None = None,
    ) -> None:
        self._validator = validator if validator else ReportValidator()
        self._renderer = renderer if renderer else ReportRenderer()
        self._pdf = pdf_export if pdf_export else PDFExport()
        self._html = html_export if html_export else HTMLExport()
        self._md = md_export if md_export else MarkdownExport()

    def process_engineering_report(
        self,
        requirements: ReportRequirements,
        profile: ReportProfile | None = None,
    ) -> ReportResult:
        """
        Compiles all engineering sections, renders multi-format exports, and validates.

        Args:
            requirements (ReportRequirements): All engineering result nodes.
            profile (ReportProfile | None): Formatting options.

        Returns:
            ReportResult: Executive summary, section text map, and exported file paths.
        """
        if profile is None:
            profile = ReportProfile()

        m_profile = requirements.mission_result.mission_profile
        category = m_profile.mission_category

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = ReportStrategyRegistry.get(strategy_name)
        target_sections = strategy.get_sections_list()

        # Define constraints
        constraints = ReportConstraints(min_required_sections=5)

        # 2. Compile all section content
        section_compilers = {
            "Executive Summary": ExecutiveSummaryCompiler(),
            "Mission Overview": MissionSectionCompiler(),
            "Configuration": ConfigurationSectionCompiler(),
            "Wing Geometry": GeometrySectionCompiler(),
            "Propulsion System": PropulsionSectionCompiler(),
            "Electrical System": ElectricalSectionCompiler(),
            "Avionics Systems": AvionicsSectionCompiler(),
            "Payload Integration": PayloadSectionCompiler(),
            "Mass Properties & CG": MassPropertiesSectionCompiler(),
            "Flight Performance": FlightPerformanceSectionCompiler(),
            "Mission Verification": VerificationSectionCompiler(),
            "Optimization Results": OptimizationSectionCompiler(),
            "CAD Output": CADSectionCompiler(),
            "Manufacturing Package": ManufacturingSectionCompiler(),
        }

        sections: Dict[str, str] = {}
        for name, compiler in section_compilers.items():
            sections[name] = compiler.compile(requirements)

        # Optionally include appendix
        if profile.include_appendix:
            sections["Appendix"] = AppendixSectionCompiler().compile(requirements)

        # 3. Compile executive summary text
        exec_summary = sections.get("Executive Summary", "")

        # 4. Render unified document body
        report_title = f"Fixed-Wing UAV Engineering Report — {category.name} Mission"
        full_doc = self._renderer.render_full_document(
            sections=sections,
            author=profile.author_name,
            title=report_title,
        )

        # 5. Export to multiple formats
        export_dir = os.path.abspath(os.path.join(".", "exports", "fixed_wing_report"))
        report_basename = f"FixedWing_{category.name.upper()}_Engineering_Report"

        exported_files: Dict[str, str] = {}
        exported_files["PDF"] = self._pdf.export(export_dir, report_basename, full_doc)
        exported_files["HTML"] = self._html.export(export_dir, report_basename, full_doc)
        exported_files["MARKDOWN"] = self._md.export(export_dir, report_basename, full_doc)

        # JSON archive
        json_path = os.path.join(export_dir, f"{report_basename}.json")
        os.makedirs(export_dir, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": report_title,
                "author": profile.author_name,
                "sections": {k: v[:200] + "..." for k, v in sections.items()},
                "engineering_statistics": {
                    "wingspan_m": requirements.wing_result.wing_geometry.span_m,
                    "aspect_ratio": requirements.wing_result.wing_geometry.aspect_ratio,
                    "static_margin": requirements.mass_result.static_margin,
                    "compliance_rating_pct": requirements.verification_result.compliance_report.compliance_score_pct,
                    "manufacturing_cost_usd": requirements.manufacturing_result.manufacturing_cost,
                },
            }, f, indent=2)
        exported_files["JSON"] = os.path.abspath(json_path)

        # 6. Compile engineering statistics summary
        wing = requirements.wing_result.wing_geometry
        eng_stats: Dict[str, Any] = {
            "wingspan_m": wing.span_m,
            "aspect_ratio": wing.aspect_ratio,
            "wing_loading_kg_m2": wing.wing_loading_kg_m2,
            "static_margin_pct": requirements.mass_result.static_margin * 100.0,
            "compliance_rating_pct": requirements.verification_result.compliance_report.compliance_score_pct,
            "manufacturing_cost_usd": requirements.manufacturing_result.manufacturing_cost,
            "total_sections_compiled": len(sections),
            "total_exports": len(exported_files),
        }

        # 7. Validate report
        warnings = self._validator.validate(
            exec_summary=exec_summary,
            sections=sections,
            min_sections=constraints.min_required_sections,
            exported_files=exported_files,
        )

        engineering_notes = [
            f"Report strategy applied: {strategy.name}.",
            f"Compiled {len(sections)} engineering chapters.",
            f"Exported to {len(exported_files)} file formats (PDF, HTML, Markdown, JSON).",
        ]

        recommendations = strategy.get_recommendations()

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
            "report_title": report_title,
        }

        return ReportResult(
            executive_summary=exec_summary,
            report_sections=sections,
            generated_reports={"full_document": full_doc},
            exported_files=exported_files,
            engineering_statistics=eng_stats,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )
