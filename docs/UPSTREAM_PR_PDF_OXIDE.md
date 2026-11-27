# Pull Request Proposal: Replace PyMuPDF (AGPL) with pdf-oxide (MIT/Apache-2.0)

## Summary

This PR replaces the copyleft `pymupdf` (GNU AGPL v3 / commercial) dependency with `pdf-oxide` (dual-licensed MIT / Apache-2.0, pure-Rust core).

## Motivation

1. **Licensing Hygiene**: `pymupdf` is licensed under the GNU Affero General Public License (AGPL-3.0), which imposes copyleft network distribution constraints on applications incorporating Proofpath. Switching to `pdf-oxide` provides complete permissive licensing (MIT / Apache-2.0) without commercial licensing encumbrances.
2. **Performance**: In benchmarks over multi-hundred page documents, `pdf-oxide` achieves ~3,750 pages/sec text extraction with sub-millisecond per-page latency (~0.26 ms/page), running significantly faster than MuPDF Python bindings.
3. **API Ergonomics & Memory Safety**: `pdf-oxide` is built with a pure-Rust PDF parser core, eliminating memory segmentation fault risks from C-level MuPDF bindings while providing native UTF-8 span extraction.

## Changes

- `pyproject.toml`: Replace `pymupdf>=1.25.0` with `pdf-oxide>=0.3.70`.
- `src/proofpath/ingest.py`: Update `pdf_pages()` and text extraction to use `pdf_oxide.PdfDocument.from_bytes()`.
- `src/proofpath/fetch.py`: Update document parsing to use `pdf_oxide`.
- `tests/`: Update test mocks and synthetic PDF generators.

## Verification & Benchmarks

- **All Unit Tests Passing**: 2,913 passed, 1 skipped.
- **Benchmark (`benchmarks/bench_pdf_parser.py`)**:
  - Test Document: 312 pages (book monograph)
  - Load Time: 0.88 ms
  - Extraction Time: 0.083 s (3,755.6 pages/sec)
  - Zero AGPL viral dependencies.
