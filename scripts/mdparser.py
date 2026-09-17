import argparse
import re
import sys
import xml.etree.ElementTree as etree
from pathlib import Path
from typing import override

import frontmatter
import markdown
from jinja2 import Template
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor


class MathInlineProcessor(InlineProcessor):
    def __init__(self, pattern: str, display: bool = False) -> None:
        super().__init__(pattern)
        self.display: bool = display

    @override
    def handleMatch(
        self, m: re.Match[str], data: str
    ) -> tuple[etree.Element | None, int, int]:
        math_content: str = m.group(1).strip()
        span: etree.Element = etree.Element("span")

        if self.display:
            span.set("class", "katex-display")
            span.text = (
                f"$${math_content}$$"  # Preserve $$ delimiters for KaTeX auto-render
            )
        else:
            span.set("class", "katex-inline")
            span.text = (
                f"${math_content}$"  # Preserve $ delimiters for KaTeX auto-render
            )

        return span, m.start(0), m.end(0)


class KaTeXExtension(Extension):
    @override
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        DISPLAY_MATH_RE: str = r"\$\$(.*?)\$\$"

        # Priority 175 ensures display math ($$) is processed BEFORE inline math ($).
        md.inlinePatterns.register(
            MathInlineProcessor(DISPLAY_MATH_RE, display=True), "katex-display", 175
        )

        INLINE_MATH_RE: str = r"\$([^\$\s]+)\$"

        # Register the inline math processor at priority 170.
        md.inlinePatterns.register(
            MathInlineProcessor(INLINE_MATH_RE, display=False), "katex-inline", 170
        )


def parse_markdown_with_meta(md_content: str):
    post = frontmatter.loads(md_content)
    metadata = post.metadata
    raw_body = post.content

    # Convert Markdown body to HTML with KaTeX extension included
    md = markdown.Markdown(extensions=["fenced_code", "tables", KaTeXExtension()])
    html_body = md.convert(raw_body)

    return metadata, html_body


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile Markdown blogs to HTML.")
    parser.add_argument("indir", type=str, help="Input directory containing .md files")
    parser.add_argument("--out", type=str, required=True, help="Output directory for .html files")
    parser.add_argument("--template", type=str, required=True, help="Path to the HTML template file")
    
    args = parser.parse_args()

    in_dir = Path(args.indir)
    out_dir = Path(args.out)
    template_path = Path(args.template)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}", file=sys.stderr)
        return 1
        
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    md_files = list(in_dir.glob("*.md"))
    if not md_files:
        print(f"WARNING: No Markdown files found in {in_dir}")
        return 0

    print(f"Found {len(md_files)} markdown files. Building...")

    for md_file in md_files:
        document = md_file.read_text(encoding="utf-8")
        
        meta, html = parse_markdown_with_meta(document)

        final_html = template.render(
            body=html,
            **meta,
        )
        
        out_file = out_dir / md_file.with_suffix(".html").name
        
        out_file.write_text(final_html, encoding="utf-8")
        print(f" ✓ Generated: {out_file.name}")

    return 0

if __name__ == "__main__":
    success_code = main()
    sys.exit(success_code)
