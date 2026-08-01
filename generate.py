#!/usr/bin/env python3
"""Regenerate the homepage (index.html) from the markdown content folders.

Scans diary/, problems/ and misc/, then fills templates/home-template.html
with the latest diary entry, Codeforces problem links grouped by contest,
and misc notes.

Usage:
    python generate.py

Run this locally to preview, or let the GitHub Actions workflow run it
automatically on every push.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "templates" / "home-template.html"
OUTPUT = ROOT / "index.html"

DIARY_DIR = ROOT / "diary"
PROBLEMS_DIR = ROOT / "problems"
MISC_DIR = ROOT / "misc"

# How many lines of a diary entry to show on the homepage.
MAX_DIARY_LINES = 12

# Files in the content folders ending with these suffixes are ignored.
IGNORED_SUFFIXES = (".html", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico")


def parse_front_matter(text):
    """Split a markdown file into (meta dict, body)."""
    meta = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        return meta, text
    block, body = match.groups()
    for line in block.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def first_heading(text):
    """Return the first '# ' heading in a markdown file, or None."""
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


# ---------------------------------------------------------------------------
# Diary
# ---------------------------------------------------------------------------

def collect_diary():
    entries = []
    for path in sorted(DIARY_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        date = meta.get("date", path.stem)
        entries.append({"path": path, "meta": meta, "body": body, "date": date})
    # Newest first; fall back to filename ordering when dates are equal.
    entries.sort(key=lambda e: (e["date"], e["path"].name), reverse=True)
    return entries


def render_diary(entries):
    if not entries:
        return {"date": "", "body": "          <p>No diary entries yet.</p>\n", "older": ""}

    latest = entries[0]
    date = html.escape(latest["date"])

    lines = [line.strip() for line in latest["body"].strip().splitlines() if line.strip()]
    excerpt = lines[:MAX_DIARY_LINES]
    paras = "".join("          <p>{}</p>\n".format(html.escape(line)) for line in excerpt)

    older = ""
    if len(entries) > 1:
        links = ", ".join(
            '<a href="/diary/{}">{}</a>'.format(
                e["path"].name, html.escape(e["meta"].get("title", e["path"].stem))
            )
            for e in entries[1:]
        )
        older = '        <p class="diary-older">Older: {}</p>\n'.format(links)

    return {"date": date, "body": paras, "older": older}


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

PROBLEM_PATTERN = re.compile(r"^(\d+)([A-Za-z]+)\.md$")


def collect_problems():
    groups = {}
    for path in PROBLEMS_DIR.glob("*.md"):
        match = PROBLEM_PATTERN.match(path.name)
        if not match:
            continue
        contest, letter = match.groups()
        groups.setdefault(contest, []).append(letter)
    # Highest contest number first, letters in alphabetical order.
    return {c: sorted(letters) for c, letters in sorted(groups.items(), key=lambda kv: int(kv[0]), reverse=True)}


def render_problems(groups):
    rows = []
    for contest, letters in groups.items():
        links = "".join(
            '<a href="/problems/{}{}.md">{}</a>'.format(contest, letter, letter)
            for letter in letters
        )
        rows.append(
            "            <div class=\"contest\">\n"
            "              <div class=\"contest-row\">\n"
            "                <span class=\"contest-label\">{}</span>\n"
            "                <span class=\"contest-links\">{}</span>\n"
            "              </div>\n"
            "            </div>".format(contest, links)
        )
    if not rows:
        rows.append(
            "            <div class=\"contest\">\n"
            "              <div class=\"contest-row\">\n"
                "                <span class=\"contest-label\">-</span>\n"
            "                <span class=\"contest-links\"><a href=\"/problems/\">none yet</a></span>\n"
            "              </div>\n"
            "            </div>"
        )
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

def collect_misc():
    items = []
    for path in sorted(MISC_DIR.glob("*")):
        if path.suffix in IGNORED_SUFFIXES or not path.is_file():
            continue
        if path.suffix == ".md":
            heading = first_heading(path.read_text(encoding="utf-8"))
            label = heading if heading else path.stem
        else:
            label = path.name
        items.append({"path": path, "label": label})
    return items


def render_misc(items):
    rows = []
    for item in items:
        label = html.escape(item["label"])
        href = "/misc/{}".format(item["path"].name)
        rows.append(
            "            <div class=\"contest\">\n"
            "              <div class=\"contest-row\">\n"
            "                <span class=\"contest-label\">{}</span>\n"
            "                <span class=\"contest-links\"><a href=\"{}\">open</a></span>\n"
            "              </div>\n"
            "            </div>".format(label, href)
        )
    if not rows:
        rows.append(
            "            <div class=\"contest\">\n"
            "              <div class=\"contest-row\">\n"
                "                <span class=\"contest-label\">-</span>\n"
            "                <span class=\"contest-links\">nothing here yet</span>\n"
            "              </div>\n"
            "            </div>"
        )
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    diary = render_diary(collect_diary())
    problems = render_problems(collect_problems())
    misc = render_misc(collect_misc())

    template = TEMPLATE.read_text(encoding="utf-8")
    page = (
        template.replace("{{diary_date}}", diary["date"])
        .replace("{{diary_body}}", diary["body"].rstrip("\n"))
        .replace("{{diary_older}}", diary["older"].rstrip("\n"))
        .replace("{{cf_sections}}", problems.rstrip("\n"))
        .replace("{{misc_sections}}", misc.rstrip("\n"))
    )

    OUTPUT.write_text(page, encoding="utf-8")
    print("Wrote {}".format(OUTPUT))


if __name__ == "__main__":
    main()
