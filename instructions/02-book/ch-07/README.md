# CHAPTER 7 Cross-Validation in Finance

**Task:** `CH-07`. **Status:** draft; independent review pending.

**Source:** [OPS/c07.xhtml](../../01-source/private/epub/OPS/c07.xhtml#Page_103); source EPUB SHA-256 `48295c01e8fef21098a10c3fa7b17eafe7830854614c5d882c978cfbceda6c7a`.

**Direct source locator:** body-iterator positions 3 to 10 (end exclusive); printed markers 103–103. These are not Word page numbers.

The complete source and pixel-level catalogs remain in the private working package. This public view preserves task IDs, locators and draft engineering interpretations, not verbatim book paragraphs or approved mathematical transcriptions.

## Description and proposed work

Define financial cross-validation, diagnose leakage and reproduce purging, embargo and scoring implementations.

## Cautions to cross-check

Interval semantics must be explicit; historical library bugs require version-qualified reproduction.

## TODO and acceptance gates

- [ ] Read the entire original span, children, lists, tables, images, notes and exercises.
- [ ] Cross-check this task description and caution; record omissions and unsupported claims.
- [ ] Inventory ordinary inline mathematics as well as equation images; verify notation and domains.
- [ ] Establish independent analytical or high-precision test oracles and boundary cases.
- [ ] Where applicable, reproduce the reference before a readable C++ implementation.
- [ ] Record numerical tolerances, measured performance, failure behavior and remaining blockers.
- [ ] Obtain distinct reviewer evidence; bind approvals to source, specification and evidence hashes.

## Direct child tasks

- [S-7.1 — 7.1 MOTIVATION](sections/7.1.md)
- [S-7.2 — 7.2 THE GOAL OF CROSS-VALIDATION](sections/7.2.md)
- [S-7.3 — 7.3 WHY K-FOLD CV FAILS IN FINANCE](sections/7.3.md)
- [S-7.4 — 7.4 A SOLUTION: PURGED K-FOLD CV](sections/7.4.md)
- [S-7.5 — 7.5 BUGS IN SKLEARN’S CROSS-VALIDATION](sections/7.5.md)
- [CH-07-exercises — EXERCISES](apparatus/exercises.md)
- [CH-07-bibliography — BIBLIOGRAPHY](apparatus/bibliography.md)
