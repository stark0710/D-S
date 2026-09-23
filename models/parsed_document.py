"""
ParsedDocument Intermediate Domain Model

Purpose:
    Defines the `ParsedDocument` domain model representing the generic, structured representation
    of a Markdown document after front matter and section parsing, prior to entity builder transformation.

Role in Architecture:
    `ParsedDocument` acts as the canonical intermediate data representation (IR) within the Markdown Parsing Engine.
    It encapsulates repository metadata, YAML front matter, parsed heading sections, and raw markdown text.
    Future `EntityBuilder` components consume `ParsedDocument` objects to instantiate concrete domain models
    (such as `EngineeringParameter`, `MissionDomain`, or `MissionCategory`) without performing file I/O or text parsing.
"""

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING
from backend.models.repository_document import RepositoryDocument

if TYPE_CHECKING:
    from backend.knowledge.parser.markdown_section_parser import MarkdownSection


@dataclass(slots=True)
class ParsedDocument:
    """
    Intermediate domain model representing a fully parsed Markdown document structure.

    Architectural Relationships:
        - `RepositoryDocument`: Encapsulates path, filename, and discovery metadata.
        - `metadata`: Contains deserialized YAML front matter key-value pairs.
        - `sections`: List of parsed section objects (forward reference to MarkdownSection).
        - `raw_markdown`: The original unparsed UTF-8 source string.
        - `EntityBuilder`: Consumes this ParsedDocument to build domain entities (`KnowledgeEntity`).

    Attributes:
        repository_document (RepositoryDocument): Originating repository document metadata.
        metadata (dict[str, Any]): Parsed YAML front matter dictionary.
        sections (list["MarkdownSection"]): Parsed Markdown sections list.
        raw_markdown (str): Complete raw UTF-8 string content of the Markdown file.
    """

    repository_document: RepositoryDocument
    metadata: dict[str, Any] = field(default_factory=dict)
    sections: list["MarkdownSection"] = field(default_factory=list)
    raw_markdown: str = ""
