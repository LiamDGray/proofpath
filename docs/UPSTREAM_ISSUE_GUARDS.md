# Issue Proposal: Epistemic Guards for Landing Pages, Abstract Contradictions, and Unindexed Literature

## Context & Motivation

During verification runs on academic manuscripts containing diverse reference types (journal articles, publisher landing pages, dissertations, and monographs), we identified three failure modes in citation audit:

1. **Defect 1 (Publisher Landing Pages Classified as Fulltext)**:
   Publisher landing pages (e.g. SAGE or Cambridge URLs containing `/doi/abs/`) contain enough boilerplate words and blurb text for HTML extractors to pass word-count thresholds, causing them to be filed as `fulltext`.
2. **Defect 2 (False REFUTED Contradictions from Abstracts)**:
   When an NLI model evaluates a claim against a publisher blurb or abstract, the absence of full text often causes the model to hallucinate a contradiction and emit `REFUTED` (`claim is not supported by the cited source`). While an abstract can confirm support (the authors' summary), it cannot legitimately refute a claim whose supporting data resides in the unread body text.
3. **Defect 3 (False GHOST Accusations on Legitimate Literature)**:
   When a citation lacks a DOI or arXiv ID (e.g., monographs, working papers, dissertations), absence in CrossRef or Semantic Scholar title search passes is not proof of fabrication. Labeling these works `GHOST REFERENCE` falsely accuses authors of fabricating citations.

## Proposed Guards

1. **D1 Landing Page Guard**: In `fetch._finish`, inspect `final_url` and downgrade URLs matching `/doi/abs/`, `/abstract` from `fulltext` to `landing`.
2. **D2 Contradiction Demotion Guard**: In `verify._verdict_finding`, refuse a `REFUTED` contradiction if `status.text_kind != "fulltext"`. Demote verdict to `NEI` with a note: `demoted from REFUTED: evidence is {text_kind}, not full text`.
3. **D3 Unindexed Literature Guard**: Expand `resolve._UNINDEXED_WORDS` to recognize `working paper`, `thesis`, `dissertation`, `monograph`, classifying missing unindexed items as `UNVERIFIED (not in bibliographic indexes)` rather than `GHOST REFERENCE`.

## Verification & Benchmarks

- **Benchmark**: `benchmarks/bench_epistemic_guards.py`
- **Unit Tests**: `tests/test_epistemic_guards.py` (all passing).
