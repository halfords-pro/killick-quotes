#!/usr/bin/env python3
"""Generate a daily Killick quote and render it into index.html and archive.html."""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
from string import Template

import anthropic

SCRIPT_DIR = Path(__file__).parent
YEAR_OFFSET = 226  # 2026 → 1800

SCENARIOS = [
    "Killick discovers weevils in the ship's biscuit and gives his opinion on the matter.",
    "Killick has been asked to serve coffee but the coffee mill is broken.",
    "Killick is trying to press the Captain's best uniform coat before a formal dinner.",
    "Killick overhears the Doctor playing his cello badly and has thoughts on the subject.",
    "Killick discovers someone has been at the Captain's private Madeira.",
    "Killick is laying out the best tablecloth and discovers a stain on it.",
    "Killick is asked to prepare the cabin for important visitors at very short notice.",
    "Killick has not had proper sleep for three watches and is asked to bring toasted cheese.",
    "Killick discovers rats have been at the Captain's stores of preserved ginger.",
    "Killick is polishing the Captain's silver and reflecting on the lack of thanks he receives.",
    "Killick is trying to keep the cabin dry during a storm while serving dinner.",
    "Killick discovers the midshipmen have borrowed the Captain's telescope without asking.",
    "Killick is mending the Captain's stockings and thinking about how many pairs he goes through.",
    "Killick has been told they will be taking on more passengers and he must prepare berths.",
    "Killick is trying to source cream for the Captain's coffee in port and finding it difficult.",
]

SYSTEM_PROMPT = """You are Preserved Killick, steward (and sometime coxswain) aboard HMS Surprise \
under Captain Jack Aubrey, in the world of Patrick O'Brian's Aubrey-Maturin novels.

You are writing a short internal monologue or spoken grumble — the kind of thing you mutter \
to yourself or say to anyone unfortunate enough to be within earshot.

Voice and mannerisms:
- You often begin sentences with "Which I..." (a Killick signature)
- You address officers as "your honour" and gentlemen as "sir"
- You say "them" instead of "those" (e.g., "them weevils")
- You trail off mid-sentence with "..." when overcome with grievance
- You are perpetually aggrieved, long-suffering, and put-upon
- You take fierce pride in your work despite constant complaint
- Your obsessions include: the best tablecloth, cream for coffee, weevils, \
the Captain's Madeira, lack of notice, lack of sleep, lack of thanks
- You occasionally reference other crew or officers (the Doctor, Mr Pullings, \
Bonden, the midshipmen) but always from your own aggrieved perspective
- You are loyal to the Captain above all else, though you'd never say so directly

Keep the monologue to 2-4 sentences. It should feel authentic to O'Brian's prose style — \
period-appropriate language, dry wit, and the particular rhythms of lower-deck speech. \
Do not use modern slang. Do not break character. Do not include quotation marks around the text. \
Do not include any preamble or attribution — just the monologue itself."""


def story_date_for(real: date) -> date:
    """Map a real-world date to an in-universe date (2026 → 1800)."""
    try:
        return real.replace(year=real.year - YEAR_OFFSET)
    except ValueError:
        # Feb 29 in a leap year that doesn't exist in the story year
        return real.replace(year=real.year - YEAR_OFFSET, day=28)


def generate_quote(scenario: str, api_key: str | None = None) -> str:
    """Call the Anthropic API to generate a Killick quote for the given scenario."""
    client = anthropic.Anthropic(**{"api_key": api_key} if api_key else {})
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": scenario}],
    )
    text = message.content[0].text.strip()
    if not text:
        raise ValueError("API returned an empty response")
    return text


def render_index(quote_text: str, story_date: date) -> None:
    """Render the daily quote into index.html using the template."""
    template_path = SCRIPT_DIR / "template.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = Template(template_str)

    date_formatted = f"{story_date.day} {story_date.strftime('%B %Y').upper()}"
    iso_date = story_date.isoformat()

    html = template.substitute(
        quote_text=escape(quote_text),
        date_formatted=date_formatted,
        iso_date=iso_date,
    )

    output_path = SCRIPT_DIR / "index.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote {output_path}")


def append_to_archive(quote_text: str, scenario: str, story_date: date) -> None:
    """Append the quote to the JSONL archive."""
    archive_path = SCRIPT_DIR / "quotes.jsonl"
    entry = {
        "date": story_date.isoformat(),
        "quote": quote_text,
        "scenario": scenario,
    }
    with open(archive_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Appended to {archive_path}")


def render_archive() -> None:
    """Render the archive page from quotes.jsonl."""
    archive_path = SCRIPT_DIR / "quotes.jsonl"
    template_path = SCRIPT_DIR / "archive_template.html"

    template_str = template_path.read_text(encoding="utf-8")
    template = Template(template_str)

    entries = []
    if archive_path.exists():
        for line in archive_path.read_text(encoding="utf-8").strip().splitlines():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Reverse chronological order
    entries.reverse()

    if not entries:
        entries_html = '<p class="empty">No grievances recorded yet. Check back tomorrow.</p>'
    else:
        parts = []
        for i, entry in enumerate(entries):
            dt = date.fromisoformat(entry["date"])
            date_str = f"{dt.day} {dt.strftime('%B %Y').upper()}"
            parts.append(
                f'<div class="entry">\n'
                f'    <p class="entry-date"><time datetime="{entry["date"]}">{date_str}</time></p>\n'
                f'    <p class="entry-quote">{escape(entry["quote"])}</p>\n'
                f'</div>'
            )
            if i < len(entries) - 1:
                parts.append('<div class="entry-divider">&#10087;</div>')
        entries_html = "\n".join(parts)

    html = template.substitute(entries=entries_html)

    output_path = SCRIPT_DIR / "archive.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a daily Killick quote.")
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)",
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    story_date = story_date_for(now.date())
    day_of_year = now.timetuple().tm_yday
    scenario = SCENARIOS[day_of_year % len(SCENARIOS)]

    print(f"Story date: {story_date.isoformat()}")
    print(f"Scenario ({day_of_year % len(SCENARIOS)}): {scenario}")

    try:
        quote_text = generate_quote(scenario, api_key=args.api_key)
    except anthropic.APIError as e:
        print(f"API error: {e}. Retrying once...")
        try:
            quote_text = generate_quote(scenario, api_key=args.api_key)
        except anthropic.APIError as e2:
            print(f"API error on retry: {e2}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error generating quote: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Quote: {quote_text}")

    render_index(quote_text, story_date)
    append_to_archive(quote_text, scenario, story_date)
    render_archive()

    print("Done.")


if __name__ == "__main__":
    main()
