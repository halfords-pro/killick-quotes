# CLAUDE.md

## Project Overview

**mybesttablecloth.com** — a static site hosted on GitHub Pages that serves a daily grievance from Preserved Killick, the perpetually aggrieved steward from Patrick O'Brian's Aubrey-Maturin novels.

A GitHub Actions workflow runs daily at 6am UTC, calls the Anthropic API (Claude Haiku) to generate a Killick monologue, renders it into `index.html`, appends it to `quotes.jsonl`, and regenerates the archive page.

## Key Files

- `generate.py` — Main script: API call, template rendering, archive management
- `template.html` — HTML/CSS template for the daily quote page (uses `string.Template`)
- `archive_template.html` — HTML/CSS template for the archive page
- `.github/workflows/killick.yml` — Daily cron workflow (6am UTC + manual dispatch)
- `quotes.jsonl` — Append-only archive of generated quotes (committed by the workflow)
- `index.html` / `archive.html` — Generated output (committed by the workflow)
- `CNAME` — Custom domain: `mybesttablecloth.com`

## Architecture

- **API model**: `claude-haiku-4-5-20251001`
- **Scenario selection**: 15 prompts, picked by `day_of_year % 15`
- **In-universe dates**: Real-world year minus 226 (2026 → 1800)
- **Templates**: Separate HTML files with `${placeholder}` substitution, not inline in Python
- **Generated files** (`index.html`, `archive.html`, `quotes.jsonl`) are committed by GitHub Actions, not checked in manually

## Design System

- Background: `#1a120a` (dark tar)
- Card: `#f4ead5` (parchment) with double rope border
- Accents: `#8b6914` (rope-gold)
- Text: `#2c1a0e` (ink)
- Fonts: IM Fell English (body), IM Fell English SC (headings) via Google Fonts
- Decorative fleurons (`❧`) as separators

## Local Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python generate.py --api-key sk-ant-...
open index.html
```

## Repository Secret

`ANTHROPIC_API_KEY` must be set as a GitHub Actions repository secret.
