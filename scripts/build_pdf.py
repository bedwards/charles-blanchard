#!/usr/bin/env python3
"""
Build a professional PDF of the complete English translation.
Uses weasyprint for high-quality PDF generation with Lexend font.
"""

import subprocess
from pathlib import Path

BASE = Path(__file__).parent.parent
TRANSLATIONS = BASE / "translations"
DOCS = BASE / "docs"
ASSETS = DOCS / "assets"

# Order of chapters for the complete book
CHAPTERS = [
    ("01_preface.txt", "Preface", "by Léon-Paul Fargue"),
    ("02_chapter_1_the_cold.txt", None, None),
    ("03_chapter_2_clogmakers_house.txt", None, None),
    ("04_supplement_first_version.txt", "Supplement to the First Version", None),
    ("05_second_version_bread.txt", "Second Version", "The Bread"),
    ("06_third_version_1_happy.txt", "Third Version", None),
    ("06_third_version_2_small_town.txt", None, None),
    ("06_third_version_3_market.txt", None, None),
    ("06_third_version_4_fair.txt", None, None),
    ("06_third_version_5_carousel.txt", None, None),
    ("07_variants.txt", "Variants", None),
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Charles Blanchard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500&display=swap');

        @page {{
            size: 6in 9in;
            margin: 0.75in 0.875in;
            @bottom-center {{
                content: counter(page);
                font-family: 'Lexend', sans-serif;
                font-size: 10pt;
                color: #666;
            }}
        }}

        @page:first {{
            @bottom-center {{ content: none; }}
        }}

        body {{
            font-family: 'Lexend', sans-serif;
            font-weight: 300;
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a1a;
            text-align: justify;
            hyphens: auto;
        }}

        .title-page {{
            page-break-after: always;
            text-align: center;
            padding-top: 2.5in;
        }}

        .title-page h1 {{
            font-size: 28pt;
            font-weight: 500;
            letter-spacing: 0.05em;
            margin-bottom: 0.5em;
        }}

        .title-page .author {{
            font-size: 14pt;
            font-weight: 400;
            margin-bottom: 2em;
        }}

        .title-page .translator {{
            font-size: 10pt;
            color: #666;
            margin-top: 3in;
        }}

        .section-title {{
            page-break-before: always;
            text-align: center;
            padding-top: 1.5in;
            margin-bottom: 2em;
        }}

        .section-title h2 {{
            font-size: 18pt;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.3em;
        }}

        .section-title .subtitle {{
            font-size: 12pt;
            font-style: italic;
            color: #444;
        }}

        .chapter-title {{
            text-align: center;
            margin: 2em 0 1.5em 0;
        }}

        .chapter-title h3 {{
            font-size: 14pt;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .chapter-title h4 {{
            font-size: 12pt;
            font-weight: 400;
            margin-top: 0.3em;
        }}

        p {{
            margin: 0;
            text-indent: 1.5em;
        }}

        p:first-of-type {{
            text-indent: 0;
        }}

        .scene-break {{
            text-align: center;
            margin: 1.5em 0;
            text-indent: 0;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>CHARLES BLANCHARD</h1>
        <div class="author">Charles-Louis Philippe</div>
        <div class="translator">
            Translated from the French<br>
            with Claude Opus 4.5<br><br>
            2026
        </div>
    </div>

{content}

</body>
</html>
"""


def process_text(text: str) -> str:
    """Convert plain text to HTML paragraphs."""
    lines = text.strip().split('\n')
    html_parts = []
    in_paragraph = False

    for line in lines:
        line = line.strip()

        # Skip page headers like "CHARLES BLANCHARD 124"
        if line.startswith('CHARLES BLANCHARD') and any(c.isdigit() for c in line):
            continue
        if line.startswith('THE COLD') and any(c.isdigit() for c in line):
            continue
        if line.startswith('PREFACE') and any(c.isdigit() for c in line):
            continue
        if line.startswith('THE CLOG-MAKER') and any(c.isdigit() for c in line):
            continue
        if line.startswith('LE FROID') and any(c.isdigit() for c in line):
            continue

        # Scene breaks (dots, asterisks, etc.)
        if line in ['...', '* * *', '• • •', '. . .'] or (len(line) < 10 and all(c in '.·•* ' for c in line)):
            if in_paragraph:
                html_parts.append('</p>')
                in_paragraph = False
            html_parts.append('<p class="scene-break">· · ·</p>')
            continue

        # Empty line = paragraph break
        if not line:
            if in_paragraph:
                html_parts.append('</p>')
                in_paragraph = False
            continue

        # Regular text
        if not in_paragraph:
            html_parts.append('<p>')
            in_paragraph = True
            html_parts.append(line)
        else:
            html_parts.append(' ' + line)

    if in_paragraph:
        html_parts.append('</p>')

    return '\n'.join(html_parts)


def build_html() -> str:
    """Build the complete HTML document."""
    content_parts = []

    for filename, section_title, section_subtitle in CHAPTERS:
        filepath = TRANSLATIONS / filename
        if not filepath.exists():
            print(f"Warning: {filepath} not found, skipping")
            continue

        text = filepath.read_text(encoding='utf-8')

        # Add section title if specified
        if section_title:
            content_parts.append(f'''
    <div class="section-title">
        <h2>{section_title}</h2>
        {f'<div class="subtitle">{section_subtitle}</div>' if section_subtitle else ''}
    </div>
''')

        # Extract chapter title from first lines
        lines = text.strip().split('\n')
        title_lines = []
        content_start = 0

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                content_start = i + 1
                break
            title_lines.append(line)

        # Check if this is a chapter (has title structure)
        if title_lines and (title_lines[0].startswith('CHAPTER') or
                           title_lines[0].startswith('PREFACE') or
                           title_lines[0].startswith('THIRD VERSION') or
                           title_lines[0].startswith('SECOND VERSION') or
                           title_lines[0].startswith('SUPPLEMENT') or
                           title_lines[0].startswith('VARIANTS') or
                           title_lines[0] in ['I', 'II', 'III', 'IV', 'V']):
            h3 = title_lines[0] if title_lines else ''
            h4 = title_lines[1] if len(title_lines) > 1 else ''

            content_parts.append(f'''
    <div class="chapter-title">
        <h3>{h3}</h3>
        {f'<h4>{h4}</h4>' if h4 else ''}
    </div>
''')
            # Process remaining content
            remaining_text = '\n'.join(lines[content_start:])
        else:
            remaining_text = text

        content_parts.append(process_text(remaining_text))

    return HTML_TEMPLATE.format(content='\n'.join(content_parts))


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)

    html_path = ASSETS / "charles_blanchard_english.html"
    pdf_path = ASSETS / "charles_blanchard_english.pdf"

    print("Building HTML...")
    html = build_html()
    html_path.write_text(html, encoding='utf-8')
    print(f"  Written: {html_path}")

    print("Generating PDF with weasyprint...")
    result = subprocess.run(
        ["weasyprint", str(html_path), str(pdf_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return 1

    print(f"  Written: {pdf_path}")
    print(f"  Size: {pdf_path.stat().st_size / 1024:.1f} KB")

    return 0


if __name__ == "__main__":
    exit(main())
