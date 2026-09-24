"""
Fixed-Wing Engineering Report Profile Subsystem

Purpose:
    Defines the `ReportProfile` class containing default header configurations.

Role in Architecture:
    `ReportProfile` sets document metadata options, author templates, and logo links.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ReportProfile:
    """
    Configuration profile defining visual formats and rendering targets.

    Attributes:
        author_name (str): Authoring engineer name (default "Torq Wings Design Studio").
        include_appendix (bool): Flag to include mathematical appendices.
        custom_logo_path (str): Optional absolute path to logo image.
        color_theme (str): Document visual style color theme ("Classic", "Midnight").
    """

    author_name: str = "Torq Wings Design Studio"
    include_appendix: bool = True
    custom_logo_path: str = ""
    color_theme: str = "Classic"
