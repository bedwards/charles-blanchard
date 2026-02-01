# Charles Blanchard

A new English translation of Charles-Louis Philippe's unfinished 1913 novel *Charles Blanchard*.

**Read online:** [bedwards.github.io/charles-blanchard](https://bedwards.github.io/charles-blanchard/)

## About the Book

*Charles Blanchard* is the final, unfinished work of Charles-Louis Philippe (1874–1909), a French novelist celebrated for his compassionate portrayals of poverty and working-class life. Left incomplete at his death from typhoid fever at age 35, the novel was published posthumously in 1913.

The book exists in multiple versions and fragments, all included in this translation:
- A preface by symbolist poet Léon-Paul Fargue
- Two main chapters following Charles's childhood
- Three distinct drafts showing Philippe's evolving vision
- Variants and alternate passages

## Project Structure

```
chapters/           # Original French text (OCR from 1913 edition)
translations/       # English translations
docs/               # Jekyll site
  _chapters/        # Markdown chapter files
  _layouts/         # HTML templates
  assets/           # CSS, audio, PDF
  about/            # About pages
scripts/            # Build scripts
audio/              # MP3 audiobook files
data/               # Original 1913 PDF scan
```

## Local Development

The site uses Jekyll and is hosted on GitHub Pages.

```bash
cd docs
bundle install
bundle exec jekyll serve
```

Then visit `http://localhost:4000/charles-blanchard/`

## Build Scripts

Generate chapter pages from translations:
```bash
python scripts/build_chapter_pages.py
```

Generate PDF:
```bash
python scripts/build_pdf.py
```

## Translation

The translation aims to preserve the meditative, circling quality of Philippe's prose—his long sentences, his personification of poverty and cold, his unsentimental compassion. See [TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md) for the full style guide.

Translated with Claude Opus 4.5.

## License

The original French text is in the public domain. The English translation is provided for personal and educational use.
