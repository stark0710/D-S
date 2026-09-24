"""
MarkdownSectionParser Subsystem

Purpose:
    Defines the `MarkdownSectionParser` class responsible for parsing raw Markdown text,
    identifying ATX heading structures (`#` through `######`), extracting section content,
    and constructing parent-child hierarchy trees.

Role in Architecture:
    `MarkdownSectionParser` converts unformatted Markdown body text into structured `MarkdownSection`
    objects. It acts as the section structural analysis component of the Markdown Parsing Engine.
"""

import re
from backend.models.markdown_section import MarkdownSection


class MarkdownSectionParser:
    """
    Parser for extracting ATX heading sections and building document section trees.

    Responsibilities:
        - Strip optional YAML front matter prior to section parsing.
        - Identify ATX-style headings (`#` through `######`).
        - Collect exact text content for each heading section.
        - Construct `parent_title` and `children` hierarchical relationships.
        - Create a synthetic `heading_level=0` section for documents lacking headings.

    Algorithm Overview:
        1. `_strip_front_matter`: Removes leading `--- ... ---` YAML block if present.
        2. `_extract_headings_and_content`: Scans line-by-line to extract `(heading_level, title, content)` tuples.
        3. `_build_hierarchy`: Uses a stack algorithm to set `parent_title` and populate `children` lists.
        4. Returns the complete list of `MarkdownSection` objects in document order.

    Limitations:
        - Structural Only: Does not parse markdown formatting inside content (bold, links, code blocks).
        - ATX Headings Only: Ignores Setext-style (`===`, `---`) headings.
    """

    # ATX Heading Regex: Matches 1 to 6 '#' followed by space and heading title
    ATX_HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.*)$")

    def parse(self, markdown_text: str) -> list[MarkdownSection]:
        """
        Parses Markdown text into a structured list of MarkdownSection objects.

        Args:
            markdown_text (str): Raw Markdown string content.

        Returns:
            list[MarkdownSection]: List of MarkdownSection objects with hierarchy populated.
        """
        if not markdown_text:
            return [self._create_synthetic_root_section("")]

        body_text = self._strip_front_matter(markdown_text)

        raw_sections = self._extract_headings_and_content(body_text)

        if not raw_sections:
            return [self._create_synthetic_root_section(body_text)]

        sections: list[MarkdownSection] = [
            MarkdownSection(
                heading_level=lvl,
                title=title,
                content=content,
                parent_title=None,
                children=[],
            )
            for lvl, title, content in raw_sections
        ]

        self._build_hierarchy(sections)
        return sections

    def _strip_front_matter(self, text: str) -> str:
        """Strips leading YAML front matter block if present."""
        stripped = text.lstrip()
        if not stripped.startswith("---"):
            return text

        content_after_first = stripped[3:]
        end_idx = content_after_first.find("\n---")
        if end_idx != -1:
            # Return text following the closing '---'
            return content_after_first[end_idx + 4:].lstrip()

        return text

    def _extract_headings_and_content(self, text: str) -> list[tuple[int, str, str]]:
        """
        Scans body text line by line to discover ATX headings and collect section content.

        Returns:
            list[tuple[int, str, str]]: List of (heading_level, title, content) tuples.
        """
        lines = text.splitlines()
        extracted: list[tuple[int, str, list[str]]] = []
        current_level: int | None = None
        current_title: str | None = None
        current_content_lines: list[str] = []

        for line in lines:
            match = self.ATX_HEADING_REGEX.match(line)
            if match:
                # Save previous section if present
                if current_title is not None and current_level is not None:
                    extracted.append((current_level, current_title, current_content_lines))

                current_level = len(match.group(1))
                current_title = match.group(2).strip()
                current_content_lines = []
            else:
                if current_title is not None:
                    current_content_lines.append(line)

        # Append final section
        if current_title is not None and current_level is not None:
            extracted.append((current_level, current_title, current_content_lines))

        # Format content by joining lines and stripping leading/trailing blank lines
        results: list[tuple[int, str, str]] = []
        for lvl, title, content_lines in extracted:
            content_str = "\n".join(content_lines).strip()
            results.append((lvl, title, content_str))

        return results

    def _build_hierarchy(self, sections: list[MarkdownSection]) -> None:
        """
        Establishes parent-child relationships using a stack to track active heading levels.

        Args:
            sections (list[MarkdownSection]): Flat list of sections to link in-place.
        """
        stack: list[MarkdownSection] = []

        for section in sections:
            # Pop stack until we find a section with a lower heading level (higher in hierarchy)
            while stack and stack[-1].heading_level >= section.heading_level:
                stack.pop()

            if stack:
                parent = stack[-1]
                section.parent_title = parent.title
                parent.children.append(section)

            stack.append(section)

    def _create_synthetic_root_section(self, content: str) -> MarkdownSection:
        """Constructs a synthetic root section for documents lacking ATX headings."""
        return MarkdownSection(
            heading_level=0,
            title="Document",
            content=content.strip(),
            parent_title=None,
            children=[],
        )
