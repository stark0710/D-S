"""
MarkdownSection Domain Model

Purpose:
    Defines the `MarkdownSection` domain model representing a single Markdown heading
    and its associated text content and structural children.

Role in Architecture:
    `MarkdownSection` is a pure structural model used within the Markdown Parsing Engine.
    It represents a single node in a Markdown document's section tree. `ParsedDocument` holds a list
    of `MarkdownSection` objects, which are later consumed by `EntityBuilder` implementations
    to extract domain-specific parameters, rules, and constraints without needing to parse text directly.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class MarkdownSection:
    """
    Domain model representing a single heading section within a Markdown document.

    Field Descriptions:
        heading_level (int): The Markdown heading depth (1 for #, 2 for ##, 3 for ###).
        title (str): Cleaned heading text.
        content (str): Text body belonging to this section until the next heading.
        parent_title (str | None): Title of the parent heading section, or None for root headers.
        children (list[MarkdownSection]): Child subsection nodes belonging to this section.

    Architectural Relationships:
        - `MarkdownSectionParser`: Builds `MarkdownSection` hierarchy trees from raw markdown text.
        - `ParsedDocument`: Stores `MarkdownSection` trees in its `sections` attribute.
        - `EntityBuilder`: Traverses `MarkdownSection` objects to populate engineering entity fields.
    """

    heading_level: int
    title: str
    content: str
    parent_title: str | None = None
    children: list["MarkdownSection"] = field(default_factory=list)
