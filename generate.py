#!/usr/bin/env python3
"""Regenerate the site from the markdown content folders.

- index.html          <- filled from templates/home-template.html
- problems/*.html     <- filled from templates/problem-template.html
- misc/*.html         <- filled from templates/misc-template.html

All files are read and written as UTF-8 (with a BOM so VS Code and other
editors always detect the encoding correctly).

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
PROBLEM_TEMPLATE = ROOT / "templates" / "problem-template.html"
MISC_TEMPLATE = ROOT / "templates" / "misc-template.html"
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


def write_utf8_bom(path, text):
    """Write text as UTF-8 with a BOM so editors detect the encoding."""
    path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Tiny markdown -> HTML converter (enough for the notes in this site)
# ---------------------------------------------------------------------------

def md_inline(text):
    """Convert inline markdown (code, links, bold, italic) to HTML."""
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def md_block_to_html(body):
    """Convert a markdown body (headings + paragraphs) to HTML blocks."""
    lines = body.splitlines()
    out = []
    para = []

    def flush():
        if para:
            out.append("<p>{}</p>".format(" ".join(md_inline(line) for line in para)))
            para.clear()

    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            flush()
            level = len(match.group(1))
            out.append("<h{0}>{1}</h{0}>".format(level, md_inline(match.group(2))))
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


def extract_title_contest(body):
    """Pull the first '# ' (title) and first '## ' (contest) heading out of a body."""
    title = None
    contest = None
    remaining = []
    for line in body.splitlines():
        m1 = re.match(r"^#\s+(.*)$", line)
        m2 = re.match(r"^##\s+(.*)$", line)
        if m1 and title is None:
            title = m1.group(1).strip()
            continue
        if m2 and contest is None:
            contest = m2.group(1).strip()
            continue
        remaining.append(line)
    return title, contest, "\n".join(remaining)


# ---------------------------------------------------------------------------
# Diary
# ---------------------------------------------------------------------------

def collect_diary():
    entries = []
    for path in sorted(DIARY_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
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
            '<a href="/problems/{}{}.html">{}</a>'.format(contest, letter, letter)
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
            heading = first_heading(path.read_text(encoding="utf-8-sig"))
            label = heading if heading else path.stem
        else:
            label = path.name
        items.append({"path": path, "label": label})
    return items


def render_misc(items):
    rows = []
    for item in items:
        label = html.escape(item["label"])
        href = "/misc/{}.html".format(item["path"].stem)
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
# Problem / misc pages
# ---------------------------------------------------------------------------

def render_problem_page(path):
    text = path.read_text(encoding="utf-8-sig")
    meta, body = parse_front_matter(text)
    if meta:
        title = meta.get("title", path.stem)
        contest = meta.get("contest", "")
        difficulty = meta.get("difficulty", "")
        tags = meta.get("tags", "")
    else:
        title, contest, body = extract_title_contest(body)
        if title is None:
            title = path.stem
        difficulty = ""
        tags = ""

    content = md_block_to_html(body)
    meta_line = " \u00b7 ".join(p for p in (contest, difficulty, tags) if p)

    page = (
        PROBLEM_TEMPLATE.read_text(encoding="utf-8-sig")
        .replace("{{title}}", html.escape(title))
        .replace("{{contest}} \u00b7 {{difficulty}} \u00b7 {{tags}}", html.escape(meta_line))
        .replace("{{content}}", content)
    )
    out = path.with_suffix(".html")
    write_utf8_bom(out, page)
    return out


def render_misc_page(path):
    text = path.read_text(encoding="utf-8-sig")
    meta, body = parse_front_matter(text)
    if meta:
        title = meta.get("title", path.stem)
        date = meta.get("date", "")
        tags = meta.get("tags", "")
    else:
        title, _, body = extract_title_contest(body)
        if title is None:
            title = path.stem
        date = ""
        tags = ""

    content = md_block_to_html(body)
    meta_line = " \u00b7 ".join(p for p in (date, tags) if p)

    page = (
        MISC_TEMPLATE.read_text(encoding="utf-8-sig")
        .replace("{{title}}", html.escape(title))
        .replace("{{date}} \u00b7 {{tags}}", html.escape(meta_line))
        .replace("{{content}}", content)
    )
    out = path.with_suffix(".html")
    write_utf8_bom(out, page)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    diary = render_diary(collect_diary())
    problems = render_problems(collect_problems())
    misc = render_misc(collect_misc())

    template = TEMPLATE.read_text(encoding="utf-8-sig")
    page = (
        template.replace("{{diary_date}}", diary["date"])
        .replace("{{diary_body}}", diary["body"].rstrip("\n"))
        .replace("{{diary_older}}", diary["older"].rstrip("\n"))
        .replace("{{cf_sections}}", problems.rstrip("\n"))
        .replace("{{misc_sections}}", misc.rstrip("\n"))
    )
    write_utf8_bom(OUTPUT, page)
    print("Wrote {}".format(OUTPUT))

    for path in sorted(PROBLEMS_DIR.glob("*.md")):
        print("Wrote {}".format(render_problem_page(path)))

    for path in sorted(MISC_DIR.glob("*.md")):
        print("Wrote {}".format(render_misc_page(path)))


if __name__ == "__main__":
    main()
