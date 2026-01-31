#!/usr/bin/env python3
"""
Split charles_blanchard.txt into separate chapter files.

Structure based on TABLE DES MATIÈRES:
- Front matter
- Préface
- Chapitre I (Le froid)
- Chapitre II (La maison du Sabotier)
- Supplément à la première version
- Seconde version (Le pain)
- Troisième version (5 sub-chapters)
- Variantes
- Table des matières
- Back matter
"""

from pathlib import Path

# Line numbers (1-indexed) for section boundaries
SECTIONS = [
    # (start_line, end_line, filename, title_en, title_fr)
    (1, 101, "00_front_matter.txt", "Front Matter", "Pages de titre"),
    (102, 904, "01_preface.txt", "Preface", "Préface"),
    (905, 1851, "02_chapter_1_the_cold.txt", "Chapter I: The Cold", "Chapitre I: Le froid"),
    (1852, 2789, "03_chapter_2_clogmakers_house.txt", "Chapter II: The Clog-maker's House", "Chapitre II: La maison du Sabotier"),
    (2790, 3069, "04_supplement_first_version.txt", "Supplement to the First Version", "Supplément à la première version"),
    (3070, 4131, "05_second_version_bread.txt", "Second Version: The Bread", "Seconde version: Le pain"),
    (4132, 4272, "06_third_version_1_happy.txt", "Third Version I: Charles Blanchard Happy", "Troisième version I: Charles Blanchard heureux"),
    (4273, 4403, "06_third_version_2_small_town.txt", "Third Version II: The Small Town", "Troisième version II: La Petite Ville"),
    (4404, 4515, "06_third_version_3_market.txt", "Third Version III: The Market", "Troisième version III: Le Marché"),
    (4516, 4637, "06_third_version_4_fair.txt", "Third Version IV: The Fair", "Troisième version IV: La Foire"),
    (4638, 4831, "06_third_version_5_carousel.txt", "Third Version V: The Carousel Horses", "Troisième version V: Les chevaux de bois"),
    (4832, 6362, "07_variants.txt", "Variants", "Variantes"),
    (6363, 6435, "08_table_of_contents.txt", "Table of Contents", "Table des matières"),
    (6436, 6637, "09_back_matter.txt", "Back Matter", "Matière finale"),
]


def split_text(input_path: Path, output_dir: Path) -> list:
    """Split the text file into chapters."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read content and split by newline (consistent with wc -l + 1)
    content = input_path.read_text(encoding="utf-8")
    # Split but preserve newlines by re-adding them
    raw_lines = content.split('\n')
    lines = [line + '\n' for line in raw_lines[:-1]]  # Add newline back
    if raw_lines[-1]:  # Handle last line without trailing newline
        lines.append(raw_lines[-1])

    results = []
    total_lines_written = 0

    for start, end, filename, title_en, title_fr in SECTIONS:
        # Convert to 0-indexed
        section_lines = lines[start - 1:end]
        section_content = "".join(section_lines)

        output_path = output_dir / filename
        output_path.write_text(section_content, encoding="utf-8")

        line_count = len(section_lines)
        word_count = len(section_content.split())
        total_lines_written += line_count

        results.append({
            "filename": filename,
            "title_en": title_en,
            "title_fr": title_fr,
            "lines": line_count,
            "words": word_count,
            "start": start,
            "end": end,
        })

        print(f"  {filename}: lines {start}-{end} ({line_count} lines, {word_count} words)")

    print(f"\nTotal lines written: {total_lines_written}")
    print(f"Total lines in source: {len(lines)}")

    return results


def generate_summary(results: list, output_path: Path) -> None:
    """Generate a markdown summary of the book structure."""

    total_words = sum(r["words"] for r in results)
    total_lines = sum(r["lines"] for r in results)

    md = f"""# Charles Blanchard - Text Organization

## Overview

**Author:** Charles-Louis Philippe
**Preface by:** Léon-Paul Fargue
**Published:** 1913, Éditions de la Nouvelle Revue Française, Paris

This is the complete text of "Charles Blanchard", extracted from a scanned PDF
of the 1913 first edition (University of Toronto library copy).

**Total:** {total_words:,} words across {total_lines:,} lines

## File Structure

The text has been split into {len(results)} files, preserving all content in reading order.

| # | File | English Title | French Title | Words |
|---|------|---------------|--------------|-------|
"""

    for i, r in enumerate(results):
        md += f"| {i} | `{r['filename']}` | {r['title_en']} | {r['title_fr']} | {r['words']:,} |\n"

    md += """
## Section Descriptions

### Front Matter (00)
Title pages, publication information, and other bibliographic data.

### Preface (01)
Léon-Paul Fargue's preface discussing Charles-Louis Philippe's life and his
relationship with his father, who inspired this work.

### Main Text - Charles Blanchard (02-03)
The primary narrative in two chapters:
- **Chapter I: The Cold** - Describes Charles Blanchard's impoverished childhood
- **Chapter II: The Clog-maker's House** - Charles's time with the clog-maker

### Supplement to the First Version (04)
Additional material from Philippe's first draft: "Solange Blanchard Sends
Charles Blanchard to Beg at Funerals"

### Second Version: The Bread (05)
An alternate version of the narrative focusing on bread and poverty.

### Third Version (06)
A more developed version divided into five parts:
1. Charles Blanchard Happy
2. The Small Town
3. The Market
4. The Fair
5. The Carousel Horses

### Variants (07)
Alternative versions and fragments of various chapters, including multiple
versions of "The Carousel Horses" and "The Market".

### Table of Contents (08)
The original table of contents from the 1913 edition.

### Back Matter (09)
Publisher advertisements, colophon, and library markings.

## Notes

- The text was OCR'd from a scanned PDF using Tesseract with French language support
- Some OCR artifacts may remain, particularly in decorative title pages
- Page numbers from the original appear as headers (e.g., "CHARLES BLANCHARD 124")
- The source file `charles_blanchard.txt` remains unchanged as the authoritative copy
"""

    output_path.write_text(md, encoding="utf-8")
    print(f"\nSummary written to: {output_path}")


def main():
    base_dir = Path(__file__).parent.parent
    input_path = base_dir / "text" / "charles_blanchard.txt"
    chapters_dir = base_dir / "chapters"
    summary_path = base_dir / "CONTENTS.md"

    if not input_path.exists():
        print(f"Error: Source file not found: {input_path}")
        return 1

    print(f"Splitting: {input_path}")
    print(f"Output directory: {chapters_dir}\n")

    results = split_text(input_path, chapters_dir)
    generate_summary(results, summary_path)

    print("\nDone!")
    return 0


if __name__ == "__main__":
    exit(main())
