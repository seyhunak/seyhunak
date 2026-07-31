# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

`seyhunak/seyhunak` is a GitHub **profile README** repository — the content rendered on https://github.com/seyhunak. There is no application, no build, no test suite, and no dependency manifest. The deliverable is `README.md`.

Files:
- `README.md` — the live profile page. Current version: AI/architecture leadership positioning, shields.io badge stack, and an auto-updated articles list.
- `blueprint.md` — the previous generation of the profile (stats cards, trophies, `<!-- BLOG-POST-LIST -->` markers, social icon row). Kept as a reference/scratch layout, not rendered anywhere. Edits to it have no user-visible effect.
- `scripts/fetch_articles.py` — pulls RSS and rewrites the articles block in `README.md`.
- `.github/workflows/update_articles.yml` — runs the script daily at 00:00 UTC and on `workflow_dispatch`, then commits as `github-actions[bot]`.
- `assets/cubes_transparent.gif` / `cubes_white.gif` — swapped via GitHub's `#gh-dark-mode-only` / `#gh-light-mode-only` URL fragments. Both must stay in sync when either is replaced.

Nearly all commit history is the bot's `Update latest articles`. Expect to rebase or pull before pushing manual edits.

## Running the article updater locally

```bash
pip install feedparser
python scripts/fetch_articles.py   # must run from the repo root — it opens "README.md" by relative path
```

It takes the 5 newest entries from each feed in the `FEEDS` list (`seyhunak.substack.com`, `medium.com/@seyhunak`), so up to 10 lines total, and overwrites the block between the marker comments in place. Add or remove a feed by editing `FEEDS` in the script; there is no config file.

## The articles block

The script rebuilds the block between the markers from scratch on every run, so it is idempotent and self-healing: a missing, duplicated, or reordered marker converges back to exactly one `<!-- ARTICLES START -->` / `<!-- ARTICLES END -->` pair. Content outside the markers is preserved verbatim.

This was previously a live bug — `README.md` had lost its END marker, and the old script's two branches alternated between appending a duplicate START and deleting the END, shuffling and dropping entries on each daily run. Both the marker and the script logic are fixed; don't reintroduce a version that requires the markers to already be well-formed.

If every feed fails to return entries, the script exits non-zero **without writing**, so a transient network or RSS outage cannot blank the list — the workflow step fails loudly instead of committing an empty block.

When editing `README.md` by hand, put manual content *outside* the markers — anything between them is overwritten on the next run.
