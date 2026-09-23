"""
Fixed-Wing CAD Output Section Compiler

Purpose:
    Defines the CAD model summary content generation.

Role in Architecture:
    `CADSectionCompiler` reviews bounding box, volume, feature tree depth, and export paths.
"""

from backend.design.fixed_wing.report.report_requirements import ReportRequirements


class CADSectionCompiler:
    """
    Compiler for the CAD Outputs chapter.
    """

    def compile(self, requirements: ReportRequirements) -> str:
        cad = requirements.cad_result

        bbox = cad.cad_metadata.bounding_box_dimensions
        content = (
            "# CAD Model Outputs\n\n"
            "The parametric 3D CAD model was generated with the following characteristics:\n"
            f"*   **Generating Backend**: {cad.cad_metadata.generating_backend}\n"
            f"*   **Bounding Box**: {bbox[0]:.2f} m × {bbox[1]:.2f} m × {bbox[2]:.2f} m "
            f"(length × span × height)\n"
            f"*   **Total Solid Volume**: {cad.cad_metadata.volume_m3:.5f} m³\n"
            f"*   **Assembly Components**: {len(cad.parts)} parts positioned\n"
            f"*   **Generation Time**: {cad.cad_metadata.generation_time_ms:.1f} ms\n\n"
            "### Exported File Formats\n"
        )
        if cad.exported_files:
            for fmt, path in cad.exported_files.items():
                content += f"*   **{fmt}**: `{path}`\n"
        else:
            content += "*   No CAD files were exported.\n"

        return content
