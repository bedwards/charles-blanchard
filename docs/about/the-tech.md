---
layout: default
title: About the Tech
permalink: /about/the-tech/
---

<nav class="about-nav">
    <a href="{{ '/about/the-book/' | relative_url }}">The Book</a>
    <a href="{{ '/about/the-translation/' | relative_url }}">The Translation</a>
    <a href="{{ '/about/the-tech/' | relative_url }}" class="active">The Tech</a>
</nav>

<div class="about-content">

# The Technical Stack

This translation was produced using a multi-agent workflow in Claude Code, with Claude Opus 4.5 doing all the work—OCR analysis, translation, site generation, and documentation. Here's how it worked.

## Source Material

### The PDF

The source is a scan of the 1913 first edition of *Charles Blanchard*, held by the University of Toronto library and digitized by the Internet Archive:

```
charlesblanchard00philuoft.pdf
268 pages, 8.2 MB
Scanned at 200-400 DPI
```

The scan included an existing OCR text layer from the Internet Archive, but with significant errors—particularly in decorative title pages and the bookplate.

### OCR Processing

We re-OCR'd the document using **ocrmypdf** with Tesseract and French language support:

```bash
ocrmypdf \
  --force-ocr \
  -l fra \
  --deskew \
  --clean \
  --sidecar output.txt \
  input.pdf output.pdf
```

Options:
- `--force-ocr`: Re-OCR even pages with existing text
- `-l fra`: French language model
- `--deskew`: Correct skewed page scans
- `--clean`: Pre-process images with unpaper
- `--sidecar`: Extract text to separate file

The result: 45,734 words, 6,637 lines of clean French text.

### Text Extraction

We also tested **pymupdf4llm** for extracting the existing text layer:

```python
import pymupdf4llm

md_text = pymupdf4llm.to_markdown(
    "input.pdf",
    write_images=False,
    page_chunks=False,
)
```

For scanned documents with older OCR, ocrmypdf produced cleaner results. For native PDFs, pymupdf4llm is faster and preserves structure better.

### Splitting into Chapters

A custom Python script split the text into chapters based on the table of contents:

```python
SECTIONS = [
    (1, 101, "00_front_matter.txt", "Front Matter"),
    (102, 904, "01_preface.txt", "Preface"),
    (905, 1851, "02_chapter_1_the_cold.txt", "Chapter I: The Cold"),
    # ... etc
]
```

Line numbers were determined by searching for chapter headers in the OCR'd text. The script preserves exact character counts to ensure no content is lost.

## The Planner → Manager → Worker Framework

The translation used a three-tier agent architecture in Claude Code.

### Planner (Research Phase)

The initial conversation researched:
- Best practices for PDF text extraction (2025-2026)
- Literary translation techniques
- LLM translation workflows
- The author Charles-Louis Philippe and his style

This produced the translation guide and style decisions.

### Manager (Orchestration)

The manager role—the main Claude Code session—handled:
- Creating git worktrees for parallel work
- Spawning worker agents for translation
- Reviewing output
- Merging completed translations
- Updating status tracking

### Worker (Translation)

Each chapter was translated by a dedicated worker agent. The worker definition (`.claude/agents/translator.md`):

```yaml
---
name: translator
description: Translates a single chapter of Charles Blanchard
tools: Read, Write, Glob
model: opus
---

[System prompt with translation rules and glossary]
```

Workers received:
- The French source file path
- The output file path
- The translation style guide (embedded in system prompt)

Workers returned:
- The completed translation
- Notes on significant translation decisions

### Git Worktree Workflow

Each translation happened in an isolated git worktree:

```bash
# Create worktree and branch
git worktree add ../charles-blanchard-ch02 -b translate/ch02

# Worker translates in worktree
# ...

# Merge when complete
git merge translate/ch02

# Cleanup
git worktree remove ../charles-blanchard-ch02
git branch -d translate/ch02
```

This allowed parallel translations without conflicts. The octopus merge for the Third Version's five parts:

```bash
git merge translate/ch06a translate/ch06b translate/ch06c \
         translate/ch06d translate/ch06e \
         -m "Merge Third Version translations (I-V)"
```

### Status Tracking

Progress was tracked in `translation_status.yaml`:

```yaml
chapters:
  - id: "02"
    file: chapters/02_chapter_1_the_cold.txt
    title: "Chapter I: The Cold"
    words: 6572
    status: done  # pending | in_progress | review | done | skip
    notes: "Core chapter - voice established"
```

The manager updated this after each merge.

## Translation with Claude Opus 4.5

### Model Selection

We used Claude Opus 4.5 for all translation work. According to 2025 benchmarks:

- Ranked #1 in WMT24 for 9/11 language pairs
- 78% "good" ratings from professional translators in blind tests
- Particularly strong for "French, German, and other European languages where wording really matters"
- Excels at "preserving tone, style, and subtle emotional nuances"

### Translation Approach

Each chapter was translated paragraph-by-paragraph (not sentence-by-sentence). Research shows this produces higher-quality literary translation by preserving document-level context.

The system prompt embedded:
- Author context (Philippe's background)
- Target voice (McCarthy, Pessoa, Orwell touchstones)
- Core translation rules (personification, rhythm, register)
- Glossary of key terms

### Output

11 chapters translated:
- ~45,000 French words → ~42,000 English words
- Total API cost: approximately $30-50

## PDF Generation

The complete English translation was compiled into a professional PDF using **weasyprint**:

```python
# HTML template with Lexend font
HTML_TEMPLATE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500&display=swap');

    @page {
        size: 6in 9in;
        margin: 0.75in 0.875in;
    }

    body {
        font-family: 'Lexend', sans-serif;
        font-weight: 300;
        font-size: 11pt;
        line-height: 1.6;
    }
</style>
...
"""

# Generate PDF
subprocess.run(["weasyprint", "input.html", "output.pdf"])
```

Design choices:
- 6×9" page size (standard trade paperback)
- Lexend font (optimized for readability, good TTS support)
- Light font weight (300) for extended reading
- Generous margins (0.75" × 0.875")
- Page numbers centered at bottom

Result: 454 KB PDF, ~200 pages.

## Audiobook Production

### ElevenLabs

Three chapters were converted to audio using ElevenLabs Studio:

- **Voice**: George (British English, warm, measured)
- **Model**: Eleven Multilingual v2
- **Format**: MP3, 128kbps

We prioritized:
1. Chapters I + II (the complete main narrative)
2. The Carousel Horses (most lyrical section)

### Post-Processing

Audio was processed in **Bitwig Studio** with:

- **Soothe2** by oeksound
  - Preset: "Soften digital tops"
  - Purpose: Reduce harshness in AI-generated speech
  - Subtle application (~2-3dB reduction in problem frequencies)

This addressed the slightly metallic quality in ElevenLabs output, particularly on sibilants and certain vowel sounds.

Final audio:
- Chapter I: 29 MB, ~30 minutes
- Chapter II: 29 MB, ~30 minutes
- Carousel Horses: 7 MB, ~7 minutes

## Website

### Jekyll on GitHub Pages

The site uses Jekyll with a minimal custom theme:

```
docs/
├── _config.yml
├── _layouts/
│   ├── default.html
│   └── chapter.html
├── _chapters/
│   └── [11 markdown files]
├── about/
│   ├── the-book.md
│   ├── the-translation.md
│   └── the-tech.md
├── assets/
│   ├── css/style.css
│   ├── audio/[3 MP3 files]
│   └── charles_blanchard_english.pdf
└── index.md
```

### Design Principles

- **Lexend font** throughout (matches PDF)
- **Minimal navigation** (Read, Listen, Download, About)
- **Clean chapter pages** optimized for Speechify/TTS
- **No JavaScript** (static HTML only)
- **Responsive** (works on mobile)

### Chapter Page Template

Each chapter page uses the `chapter` layout:

```yaml
---
layout: chapter
title: "Chapter I"
subtitle: "The Cold"
prev: /chapters/01-preface/
next: /chapters/03-chapter-2-clogmakers-house/
---
```

Navigation between chapters, clean typography, no distractions.

## Project Structure

Final repository layout:

```
charles-blanchard/
├── .claude/
│   └── agents/
│       └── translator.md      # Worker agent definition
├── audio/                      # Source audio files
├── chapters/                   # French source (split)
├── data/
│   └── charlesblanchard00philuoft.pdf  # Original scan
├── docs/                       # GitHub Pages site
├── scripts/
│   ├── extract_text.py        # OCR extraction
│   ├── split_chapters.py      # Chapter splitting
│   └── build_pdf.py           # PDF generation
├── text/
│   └── charles_blanchard.txt  # Complete French text
├── translations/               # English translations
├── CONTENTS.md                 # Book structure summary
├── TRANSLATION_GUIDE.md        # Style guide
├── WORKFLOW.md                 # Git workflow documentation
└── translation_status.yaml    # Progress tracking
```

## Reproducibility

To reproduce this translation:

1. **Get the source**: Download `charlesblanchard00philuoft.pdf` from Internet Archive
2. **OCR**: `ocrmypdf --force-ocr -l fra --deskew --clean --sidecar text.txt input.pdf output.pdf`
3. **Split chapters**: `python scripts/split_chapters.py`
4. **Configure agent**: Copy `.claude/agents/translator.md` and `TRANSLATION_GUIDE.md`
5. **Translate**: In Claude Code, spawn translator agent for each chapter
6. **Generate PDF**: `python scripts/build_pdf.py`
7. **Build site**: `cd docs && jekyll serve`

The complete project is available on GitHub.

---

*Built in one session, January 2026.*

</div>
