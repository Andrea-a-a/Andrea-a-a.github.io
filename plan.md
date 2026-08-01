# Redesign Plan

## Goal

Keep the site simple to maintain while making it feel more like a real blog.

The site should mainly contain:

- Problem notes
- Diary entries
- Misc notes such as the C++ cheatsheet

The first priority is maintenance, not layout polish.

Updating a problem note, writing a diary entry, or adding a misc note should stay as close as possible to:

1. create or edit one markdown file
2. add the right metadata
3. let the homepage or index pick it up automatically

## Content Structure

Use folders to separate content by type:

- `problems/` for Codeforces and other problem writeups
- `diary/` for diary entries, one markdown file per post
- `misc/` for reference notes such as cheatsheets

Keep each folder flat unless a nested structure is clearly needed later.

That way, the site stays easy to browse and the file paths stay obvious.

## Problem Notes

Standardize each problem note so it is easy to sort and filter later.

Each problem file should include metadata for:

- title
- contest or source
- difficulty
- tags
- status if needed

This will let the homepage and archive pages show problem cards without manual editing.

The problem note template should stay stable so new writeups only need copy, paste, and edit.

## Diary

Write each diary entry in its own markdown file.

The homepage should always show:

- the latest diary entry
- a short preview or excerpt
- the date

That keeps the diary section current without needing to edit the homepage every time.

Adding a new diary entry should never require touching old diary files.

Only the newest entry needs to be discovered for the homepage.

## Homepage

Make the homepage simple and readable.

Planned sections:

- short self-introduction or about section
- short intro or title
- latest diary entry only
- recent problem notes
- quick links to misc notes

The homepage should act as an index, not as a full app.

The diary area on the homepage should only surface the newest entry, with older entries kept in the diary archive instead of being listed on the front page.

The homepage should not duplicate content that already lives in the folders.

It should only summarize and link out.

## Maintenance Rules

Keep the system easy to maintain by following a few rules:

- Use markdown for all content
- Avoid adding a database or heavy framework
- Keep file names consistent
- Keep metadata fields consistent across problem notes
- Only update the homepage layout when the structure changes
- Prefer one source of truth per piece of content
- Keep navigation generated from folders or metadata, not manual lists when possible
- Make the default workflow feel like "add a file, done"

## Build Steps

1. Keep the current problem notes in `problems/`.
2. Create a `diary/` folder and move diary content into separate markdown files.
3. Create a `misc/` folder for cheatsheets and other reference notes.
4. Define one front matter template for problem notes and one for diary entries.
5. Decide how the homepage will find the latest diary entry automatically.
6. Decide how tags and difficulty will be stored so filtering does not need manual updates.
7. Update the homepage to summarize content instead of duplicating it.
8. Add a simple archive or index page for browsing problems by tag and difficulty.
9. Refine spacing, typography, and navigation only after the structure is stable.

## Editing Workflow

Keep the authoring workflow simple:

- Problem note: create a new markdown file in `problems/`, fill the metadata, write the solution note
- Diary entry: create a new markdown file in `diary/`, and it should appear as the latest entry automatically
- Misc note: create a markdown file in `misc/`, link it from the homepage or a misc index only if needed

If a change requires editing many files by hand, the plan should be adjusted so that content is easier to add.

## Later Improvements

If the simple version works well, possible upgrades are:

- tag filters for problem notes
- a difficulty index
- a diary archive page
- a cleaner post template

These should stay optional so the site does not become hard to manage.