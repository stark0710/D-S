"""
Fixed-Wing Manufacturing Package Section Compiler

Purpose:
    Defines the manufacturing readiness content generation.

Role in Architecture:
    `ManufacturingSectionCompiler` reviews BOM counts, unit costs, and fabrication file inventories.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class ManufacturingSectionCompiler:
    """
    Compiler for the Manufacturing Package chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        mfg = requirements.manufacturing_result

        content = (
            "# Manufacturing Package\n\n"
            "The production package was compiled with the following deliverables:\n"
            f"*   **BOM Items**: {len(mfg.bill_of_materials)} line items\n"
            f"*   **Unit Cost Estimate**: {mfg.manufacturing_cost:.2f} USD\n"
            f"*   **Engineering Drawings**: {len(mfg.manufacturing_drawings)} sheets\n"
            f"*   **Assembly Guides**: {len(mfg.assembly_documents)} documents\n"
            f"*   **Fabrication Files**: {len(mfg.fabrication_files)} exports "
            f"({', '.join(mfg.fabrication_files.keys()) if mfg.fabrication_files else 'none'})\n"
            f"*   **QA Checklist Items**: {len(mfg.quality_checklist)}\n"
        )
        return content
