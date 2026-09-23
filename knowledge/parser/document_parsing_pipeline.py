"""
DocumentParsingPipeline Orchestration Subsystem

Purpose:
    Defines the `DocumentParsingPipeline` class responsible for orchestrating the reading,
    metadata extraction, and section parsing of a `RepositoryDocument` into a `ParsedDocument`.

Role in Architecture:
    `DocumentParsingPipeline` serves as the high-level orchestration pipeline within the Markdown
    Parsing Engine. It relies on Dependency Injection to coordinate `DocumentReader`, `FrontMatterParser`,
    and `MarkdownSectionParser` without implementing parsing algorithms or filesystem operations itself.
"""

from backend.models.repository_document import RepositoryDocument
from backend.models.parsed_document import ParsedDocument
from backend.knowledge.parser.document_reader import DocumentReader
from backend.knowledge.parser.front_matter_parser import FrontMatterParser
from backend.knowledge.parser.markdown_section_parser import MarkdownSectionParser


class DocumentParsingPipeline:
    """
    Orchestrator that converts a RepositoryDocument into a ParsedDocument intermediate representation.

    Workflow:
        1. Read raw UTF-8 text from disk using `DocumentReader`.
        2. Extract YAML front matter metadata dictionary using `FrontMatterParser`.
        3. Extract heading structure and content tree using `MarkdownSectionParser`.
        4. Construct and return a unified `ParsedDocument` instance.

    Design Principles:
        - Dependency Injection: Collaborators are passed via constructor.
        - Single Responsibility Principle (SRP): Responsible exclusively for workflow orchestration.
        - Clean Architecture: Decouples file I/O and parsing logic into injected components.
    """

    def __init__(
        self,
        reader: DocumentReader,
        front_matter_parser: FrontMatterParser,
        section_parser: MarkdownSectionParser,
    ) -> None:
        """
        Initializes the DocumentParsingPipeline with required collaborator dependencies.

        Args:
            reader (DocumentReader): Injected document file reader.
            front_matter_parser (FrontMatterParser): Injected YAML front matter parser.
            section_parser (MarkdownSectionParser): Injected Markdown section parser.
        """
        self._reader: DocumentReader = reader
        self._front_matter_parser: FrontMatterParser = front_matter_parser
        self._section_parser: MarkdownSectionParser = section_parser

    def parse(self, document: RepositoryDocument) -> ParsedDocument:
        """
        Executes the full parsing workflow for a single RepositoryDocument.

        Args:
            document (RepositoryDocument): Originating repository document metadata object.

        Returns:
            ParsedDocument: Canonical intermediate representation containing metadata, sections, and raw text.
        """
        # Step 1: Read raw markdown text
        raw_markdown = self._reader.read(document)

        # Step 2: Parse YAML front matter metadata
        metadata = self._front_matter_parser.parse(raw_markdown)

        # Step 3: Parse heading sections and build hierarchy tree
        sections = self._section_parser.parse(raw_markdown)

        # Step 4: Construct and return unified ParsedDocument
        return ParsedDocument(
            repository_document=document,
            metadata=metadata,
            sections=sections,
            raw_markdown=raw_markdown,
        )
