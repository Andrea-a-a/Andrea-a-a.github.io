# Modernization Plan

## Goal

Turn the current markdown-heavy GitHub Pages site into a cleaner, more modern personal site without losing the low-maintenance writing workflow.

The site should still feel easy to update: write markdown, commit, publish. The redesign should improve the look, readability, and structure, not add unnecessary complexity.

The content should stay in markdown. HTML, CSS, and a small amount of scripting should handle the layout, cards, navigation, and automatic indexes.

## Tech Direction

Keep markdown as the source of truth for all content, but wrap it in a thin HTML-based presentation layer.

Recommended direction:

- Markdown files for notes, diary posts, and problem writeups
- HTML templates or generated HTML pages for structure and layout
- CSS for the modern visual style
- Small scripts only where automation is needed for indexes or latest-post selection
- Deployed to GitHub Pages
- No database
- No heavy backend
- Simple front matter for metadata
- Shared layout components for homepage, archive pages, and post pages

This keeps the authoring workflow lightweight while allowing a more polished UI, better navigation, and automatic indexes.

## Content Model

Organize content by purpose:

- `problems/` for problem writeups
- `diary/` for diary posts
- `misc/` for reference notes and cheatsheets

Each type should use consistent front matter so the site can build cards, lists, and archives automatically.

Suggested metadata fields:

- title
- date
- summary or excerpt
- tags
- category
- status or difficulty when relevant

## Pages

The site should have a small set of clear pages:

- Homepage
- Diary archive
- Problem archive
- Misc notes index
- Individual post pages

The homepage should not try to contain everything. It should highlight the most recent or most important content and link out to the rest.

The page chrome should come from shared HTML templates so the site feels consistent without forcing the content itself out of markdown.

## Homepage Structure

The homepage should feel more like a personal dashboard than a markdown dump.

Planned sections:

- short intro / identity section
- featured latest diary entry
- recent problem notes
- quick links to notes or reference pages
- small about / tech summary block

The page should use cards, spacing, and visual hierarchy instead of long plain text blocks.

## Visual Direction

The design should look intentional and current.

Goals:

- stronger typography hierarchy
- more whitespace and rhythm
- card-based content blocks
- subtle color accents
- responsive layout that works on mobile and desktop
- cleaner navigation and section anchors

Avoid the default markdown look and feel by giving the site a stronger layout, custom spacing, and a clear visual system.

## Implementation Stages

1. Keep the existing markdown content intact.
2. Define the page structure and metadata conventions.
3. Build shared HTML layouts for the homepage, archives, and post pages.
4. Add CSS for readability, spacing, and hierarchy.
5. Add any small scripts needed for indexes or latest-entry discovery.
6. Wrap or render the existing markdown content through the new templates.
7. Check that the site still deploys cleanly to GitHub Pages.

## Non-Goals

This redesign should not turn the site into a full CMS or a complex app.

Do not add:

- a database
- user accounts
- editing in the browser
- heavy client-side frameworks unless they are clearly needed
- content editing in HTML instead of markdown

## Success Criteria

The redesign is good enough when:

- the homepage looks polished on first load
- diary, problem, and misc content are easy to browse
- adding a new markdown file is still simple
- metadata drives the indexes instead of manual maintenance
- the site reads clearly on both desktop and mobile

## Next Step

After this plan is approved, the next step should be to choose the exact build approach and then start implementing the HTML templates and markdown rendering flow.