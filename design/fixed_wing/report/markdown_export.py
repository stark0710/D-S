"""
Fixed-Wing Markdown Export Service

Purpose:
    Defines the `MarkdownExport` class that writes report content to a Markdown file.

Role in Architecture:
    `MarkdownExport` writes the raw rendered content directly as a `.md` file.
"""

import os


class MarkdownExport:
    """
    Markdown document exporter.
    """

    def export(self, output_dir: str, filename: str, content: str) -> str:
        """
        Writes the rendered report to a Markdown file.

        Returns:
            str: Absolute path to the exported Markdown file.
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.abspath(filepath)
