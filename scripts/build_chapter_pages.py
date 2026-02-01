#!/usr/bin/env python3
"""
Generate Jekyll chapter pages from translation files.
"""

from pathlib import Path
import re

BASE = Path(__file__).parent.parent
TRANSLATIONS = BASE / "translations"
CHAPTERS_DIR = BASE / "docs" / "_chapters"

CHAPTERS = [
    ("01_preface.txt", "01-preface", "Preface", "by Léon-Paul Fargue", None, "/chapters/02-chapter-1-the-cold/"),
    ("02_chapter_1_the_cold.txt", "02-chapter-1-the-cold", "Chapter I", "The Cold", "/chapters/01-preface/", "/chapters/03-chapter-2-clogmakers-house/"),
    ("03_chapter_2_clogmakers_house.txt", "03-chapter-2-clogmakers-house", "Chapter II", "The Clog-maker's House", "/chapters/02-chapter-1-the-cold/", "/chapters/04-supplement/"),
    ("04_supplement_first_version.txt", "04-supplement", "Supplement to the First Version", None, "/chapters/03-chapter-2-clogmakers-house/", "/chapters/05-second-version/"),
    ("05_second_version_bread.txt", "05-second-version", "Second Version", "The Bread", "/chapters/04-supplement/", "/chapters/06a-third-version-1/"),
    ("06_third_version_1_happy.txt", "06a-third-version-1", "Third Version I", "Charles Blanchard Happy", "/chapters/05-second-version/", "/chapters/06b-third-version-2/"),
    ("06_third_version_2_small_town.txt", "06b-third-version-2", "Third Version II", "The Small Town", "/chapters/06a-third-version-1/", "/chapters/06c-third-version-3/"),
    ("06_third_version_3_market.txt", "06c-third-version-3", "Third Version III", "The Market", "/chapters/06b-third-version-2/", "/chapters/06d-third-version-4/"),
    ("06_third_version_4_fair.txt", "06d-third-version-4", "Third Version IV", "The Fair", "/chapters/06c-third-version-3/", "/chapters/06e-third-version-5/"),
    ("06_third_version_5_carousel.txt", "06e-third-version-5", "Third Version V", "The Carousel Horses", "/chapters/06d-third-version-4/", "/chapters/07-variants/"),
    ("07_variants.txt", "07-variants", "Variants", None, "/chapters/06e-third-version-5/", None),
]


def clean_text(text: str) -> str:
    """Convert plain text to markdown-friendly format."""
    lines = text.strip().split('\n')
    result = []

    # Skip header lines (chapter titles - we put those in frontmatter)
    content_started = False
    blank_count = 0

    for line in lines:
        stripped = line.strip()

        # Skip page headers like "CHARLES BLANCHARD 124"
        if re.match(r'^(CHARLES BLANCHARD|THE COLD|PREFACE|THE CLOG-MAKER|LE FROID|VARIANTS|THE BREAD|THE MARKET|THE FAIR|THE SMALL TOWN|THE CAROUSEL|THIRD VERSION|SECOND VERSION|SUPPLEMENT)\s*\d+$', stripped):
            continue
        if re.match(r'^(CHAPTER|PRÉFACE|CHAPITRE)\s', stripped):
            content_started = True
            continue
        if stripped in ['I', 'II', 'III', 'IV', 'V', 'THE COLD', 'THE BREAD', 'PREFACE', 'VARIANTS',
                        'THE CLOG-MAKER\'S HOUSE', 'THE MARKET', 'THE FAIR', 'THE SMALL TOWN',
                        'THE CAROUSEL HORSES', 'CHARLES BLANCHARD HAPPY',
                        'SUPPLEMENT TO THE FIRST VERSION']:
            content_started = True
            continue

        # Scene breaks
        if stripped in ['...', '* * *', '• • •', '. . .'] or (len(stripped) < 10 and stripped and all(c in '.·•* ' for c in stripped)):
            if result and result[-1] != '':
                result.append('')
            result.append('<p class="scene-break">· · ·</p>')
            result.append('')
            blank_count = 0
            continue

        # Blank lines become paragraph breaks
        if not stripped:
            blank_count += 1
            if blank_count <= 2 and result and result[-1] != '':
                result.append('')
            continue

        blank_count = 0
        content_started = True
        result.append(stripped)

    return '\n\n'.join(para for para in '\n'.join(result).split('\n\n') if para.strip())


def main():
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

    for src_file, slug, title, subtitle, prev_url, next_url in CHAPTERS:
        src_path = TRANSLATIONS / src_file
        if not src_path.exists():
            print(f"Warning: {src_path} not found")
            continue

        text = src_path.read_text(encoding='utf-8')
        content = clean_text(text)

        # Build frontmatter
        frontmatter = f"""---
layout: chapter
title: "{title}"
"""
        if subtitle:
            frontmatter += f'subtitle: "{subtitle}"\n'
        if prev_url:
            frontmatter += f'prev: {prev_url}\n'
        if next_url:
            frontmatter += f'next: {next_url}\n'
        frontmatter += "---\n\n"

        out_path = CHAPTERS_DIR / f"{slug}.md"
        out_path.write_text(frontmatter + content, encoding='utf-8')
        print(f"  {out_path.name}")

    print(f"\nGenerated {len(CHAPTERS)} chapter pages")


if __name__ == "__main__":
    main()
