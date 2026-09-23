"""
Fixed-Wing PDF Export Service

Purpose:
    Defines the `PDFExport` class that writes report content to a PDF file.

Role in Architecture:
    `PDFExport` simulates PDF generation by writing text-based PDF content.
"""

import os


class PDFExport:
    """
    PDF document exporter.
    """

    def export(self, output_dir: str, filename: str, content: str) -> str:
        """
        Writes the rendered report to a PDF file.

        Returns:
            str: Absolute path to the exported PDF file.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.pdf")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"%PDF-1.4\n% Torq Wings Engineering Report\n{content}\n%%EOF\n")
        return os.path.abspath(filepath)
