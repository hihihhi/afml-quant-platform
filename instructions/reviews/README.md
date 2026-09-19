# Authored book reviews

Generated source-locator tasks live in `instructions/02-book/`. Authored analysis
is stored separately here so regeneration cannot overwrite it or silently change
the source projection. A note is not an independent approval record.

## Current authored work

[Chapter 1](ch-01/REVIEW_NOTES.md) has a source-ordered first pass covering its 29
tasks, both tables, all eleven FAQ questions and eight exercises. Its
[SOURCE_COVERAGE.json](ch-01/SOURCE_COVERAGE.json) binds the note hash, source hash,
task IDs and original locators. CI checks that mapping, not the truth of every
interpretation. Independent review remains open.

Read parent context before processing children; approve a parent only after its
required children have passed the review protocol. Do not mistake the chapter
heading's direct source span for the entire chapter: the private task packet
contains the complete XHTML document to preserve context.
