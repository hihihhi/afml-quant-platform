# Rebuild the complete private source package

The public repository now includes the source-inventory, Word-export, full Markdown
and independent cross-check implementations. No online book download is performed.
Use your supplied EPUB; a different edition fails the SHA-256 lock.

## Commands from the repository root

```bash
python -m pip install -r instructions/requirements-dev.txt
python instructions/tools/install_source.py /path/to/advances-in-financial-machine-learning.epub
python instructions/tools/rebuild_private_source.py --name source-v1
python instructions/tools/build_task_context.py CH-01
```

Run `install_source.py` only once for a checkout. An already installed source is
retained; the installer refuses replacement. For another rebuild, choose a new
name rather than modifying an existing output. No GitHub credentials or broker
connections are needed for these commands.

The complete rebuilt package is under:

```text
instructions/01-source/private/rebuilds/source-v1/
├── REBUILD_RESULT.json
├── PRIVATE_SOURCE_NOTICE.md
└── instructions/
    ├── 00-governance/                 Exact prompt/requirement copies
    ├── 01-source/                     Full inventories and extraction reports
    │   └── private/
    │       ├── original.epub
    │       ├── epub/                  Original XHTML, CSS, images and assets
    │       └── AFML_Source_Transcription.docx
    ├── 02-book/                       All 1,138 source-rich draft task files
    ├── 03-crosschecks/                Preserved review rules and errata
    └── reports/                      Independent preservation cross-checks
```

The outer private directory is ignored by Git. Its source-rich Markdown includes
verbatim anchor paragraphs, hidden mathematical markup and links to original
assets, so it must not be copied into the public `instructions/02-book/` directory.
Public task IDs and paths are preserved as a separate source-free projection.

## What the build checks

The inventory reads every EPUB spine document and retains source bytes, heading
hierarchy, page markers, images, mathematical markup, tables and code. Word embeds
original equation/code images without OCR. Full task descriptions reuse the locked
public catalog, not a second independently edited blueprint. A separate parser
compares the original source, Word, task metadata, links and image pixels.

The wrapper refuses an incorrect EPUB, altered catalog/authority, unsafe build
name, symlink output parent, incomplete section map or an existing output name.
An audit failure prevents publication of the fresh private output directory.
Source snippets and links are never executed or followed by extraction.

**An audit pass is not mathematical or semantic approval.** Word is reflowed, not
a publisher-page facsimile; equations preserved as images are not editable math.
The generated Word file must be rendered and every page visually inspected before
being delivered as a new final transcription. This tool deliberately reports that
visual review as pending. Different DOCX container timestamps can change the file
hash even when source-preservation checks pass; do not silently replace the retained
original Word hash in `PUBLICATION_LOCK.json`.

## Tests and source integration

Public CI uses a small original synthetic EPUB with ordinary text, math markup,
an equation image, a native code block, nested lists and a native table. It tests
round-trip preservation, malicious archive paths, source tampering and output
boundaries without requiring the licensed book.

The actual uploaded EPUB was also rebuilt locally. See
[the actual-source integration record](../reports/private-rebuild-integration.json).
Its structural result is not re-labeled as a public CI or visual-layout result.
