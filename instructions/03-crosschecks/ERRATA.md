# Source discrepancy and errata register

Original content remains unchanged. These are local findings for the uploaded
edition, not an official publisher errata list. No author/publisher confirmation
has been obtained. No correction has been silently incorporated into a book method.

## ERR-0001 — covariance sample-count claim

**Source:** section 16.3, `OPS/c16.xhtml`, printed markers 222–223;
original equation image `OPS/images/c16_ILM0001.gif` and its hidden MathML.
The source image was visually read. It says one half times N times (N + 1).

**Original claim:** the paragraph presents N(N+1)/2 IID observations as a minimum
needed to estimate a nonsingular covariance matrix of dimension N, followed by a
50-variable/five-year illustration. Preserve the paragraph and image as supplied.

**Local verification:** for the ordinary centered unbiased sample covariance,
consider N=3 variables and n=4 observations:

```text
(0, 0, 0)
(1, 0, 0)
(0, 1, 0)
(0, 0, 1)
```

The mean is (1/4, 1/4, 1/4). The covariance is

```text
[ 1/4   -1/12  -1/12 ]
[-1/12   1/4   -1/12 ]
[-1/12  -1/12   1/4  ]
```

Its determinant is exactly **1/108 > 0**, although 4 < 3(3+1)/2 = 6.
The observations can occur under IID sampling from a distribution supported on
these four points. Thus the asserted universal minimum is false for this estimator.
`system/reference/covariance_counterexample.py` uses exact rational arithmetic;
its tests check the entries, determinant, and the inequality without floating error.

**Proposed clarification, not yet approved:** for centered sample covariance,
rank(S) <= min(N, n−1), so n >= N+1 is necessary. Full affine span of the observed
points is additionally needed for full rank. Having N+1 observations does **not**
mean that covariance is estimated accurately or that portfolio optimization is
reliable. Do not conflate an algebraic rank condition with statistical adequacy.

**Scope:** the paragraph's asserted sample-count lower bound. This finding does
not invalidate the surrounding concern about conditioning or justify changing HRP.

**Status:** exact local counterexample tested; independent reviewer and author
confirmation absent; correction adoption remains blocked. Keep source-fidelity and
correction tests separate. This is not approval of chapter 16 as a whole.

## ERR-0002 — source heading spelling

**Source:** section 19.6.1 is headed `Distibution of Order Sizes` in the uploaded
edition. The generated task keeps `Distibution` verbatim.

**Proposed correction:** `Distribution of Order Sizes`. This is a typography-only
proposal, not an algorithm change. Source spelling preserved; publisher confirmation
not obtained. Do not rename source IDs or silently normalize heading text.

## Source limitations (not mathematical errata)

Two equation images have no matched hidden MathML in this EPUB:
`c13_M0007a.gif` (section 13.5.1) and `c18_M0018.gif` (section 18.4). Their original
pixels remain available. Editable transcription needs direct visual review.

The EPUB has 338 explicit page markers, including 328 numeric markers. There are
38 unmarked numeric labels between 1 and 366. This is a limitation of page-boundary
reconstruction, not proof that 38 pages of text are absent. See the cross-check report.

There are 100 snippet headings, but 98 code-image placements: two snippets use native
preformatted text. A count difference must be investigated, not automatically labeled
as missing code. All native text and image placements are retained in Word/source.
