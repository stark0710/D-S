"""
Fixed-Wing HTML Export Service

Purpose:
    Defines the `HTMLExport` class that writes report content to an HTML file.

Role in Architecture:
    `HTMLExport` wraps rendered Markdown content in an HTML5 document shell.
"""

import os


class HTMLExport:
    """
    HTML document exporter.
    """

    def export(self, output_dir: str, filename: str, content: str) -> str:
        """
        Writes the rendered report to an HTML file.

        Returns:
            str: Absolute path to the exported HTML file.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.html")

        html = (
            "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
            "<meta charset=\"UTF-8\">\n"
            f"<title>Torq Wings Engineering Report</title>\n"
            "<style>body{font-family:sans-serif;max-width:900px;margin:auto;padding:2em;}"
            "h1{color:#1a237e;}h2{color:#283593;}h3{color:#3949ab;}"
            "pre{background:#f5f5f5;padding:1em;border-radius:4px;}</style>\n"
            "</head>\n<body>\n"
        )
        # Simple Markdown-to-HTML conversion for headers and bullets
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("# "):
                html += f"<h1>{stripped[2:]}</h1>\n"
            elif stripped.startswith("## "):
                html += f"<h2>{stripped[3:]}</h2>\n"
            elif stripped.startswith("### "):
                html += f"<h3>{stripped[4:]}</h3>\n"
            elif stripped.startswith("*   "):
                html += f"<li>{stripped[4:]}</li>\n"
            elif stripped == "---":
                html += "<hr>\n"
            elif stripped:
                html += f"<p>{stripped}</p>\n"

        html += "</body>\n</html>\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return os.path.abspath(filepath)
