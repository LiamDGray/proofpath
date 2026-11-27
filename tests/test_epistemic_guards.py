"""Unit tests for proofpath epistemic guards D1, D2, and D3."""

import re
import pytest
from proofpath.config import Config
from proofpath.fetch import Fetcher, _Response, Outcome
from proofpath.document import Claim, Reference, Locator
from proofpath.models import Verdict, Label, Passage
from proofpath.report import SourceStatus, Kind
from proofpath.verify import _verdict_finding
from proofpath.resolve import looks_unindexed, classify, Candidate, State


def test_d1_landing_page_guard():
    """D1 Guard: URL containing /doi/abs/ should not be returned as fulltext."""
    fetcher = Fetcher(config=Config())
    resp = _Response(
        status=200,
        content_type="text/html",
        body=b"<html><head><title>Abstract</title></head><body>This is a publisher blurb and abstract</body></html>",
        final_url="https://journals.sagepub.com/doi/abs/10.1177/00010203040506",
    )
    fetched = fetcher._finish("https://journals.sagepub.com/doi/abs/10.1177/00010203040506", 1, resp, "fulltext", [])
    # Must not remain fulltext
    assert fetched.text_kind != "fulltext"
    assert fetched.text_kind in ("landing", "abstract")
    assert any("landing" in n.lower() for n in fetched.notes)


def test_d2_refuted_demotion_when_not_fulltext():
    """D2 Guard: A REFUTED verdict with only abstract/landing page must be demoted to NEI."""
    claim = Claim(
        paragraph=1,
        sentence=1,
        locator=Locator(line=1, column=1, page=1),
        text="Technological changes cause political shifts.",
        cited_refs=(1,),
    )
    ref = Reference(number=1, locator=Locator(line=10, column=1, page=1), raw="Smith, J. 2020. Tech Shifts.")
    verdict = Verdict(
        label=Label.REFUTED,
        score=0.9,
        passage=Passage(text="Text that contradicts", source_id="doi:10.1000/1", index=0),
        reason="contradiction found",
        tier="high",
    )
    
    # Case 1: text_kind is abstract
    status_abstract = SourceStatus(
        reference=ref,
        resolve=None,
        retraction=None,
        source_id="doi:10.1000/1",
        text_kind="abstract",
        state="",
        fetch_step=1,
        url="https://doi.org/10.1000/1",
        from_cache=False,
    )
    finding = _verdict_finding(claim, status_abstract, verdict)
    assert finding is not None
    assert finding.kind == Kind.NEI
    assert any("demoted from REFUTED" in d for d in finding.detail)

    # Case 2: text_kind is fulltext (should remain NOT_SUPPORTED)
    status_fulltext = SourceStatus(
        reference=ref,
        resolve=None,
        retraction=None,
        source_id="doi:10.1000/1",
        text_kind="fulltext",
        state="",
        fetch_step=1,
        url="https://doi.org/10.1000/1",
        from_cache=False,
    )
    finding_full = _verdict_finding(claim, status_fulltext, verdict)
    assert finding_full is not None
    assert finding_full.kind == Kind.NOT_SUPPORTED


def test_d3_unindexed_monograph_guard():
    """D3 Guard: References indicating working papers, monographs, or theses are NOT_INDEXED, not GHOST."""
    raw_monograph = "Arendt, H. 1951. The Origins of Totalitarianism. Monograph series."
    raw_working_paper = "Jones, R. 2021. Epistemic Trust. Working paper 42."
    
    assert looks_unindexed(raw_monograph) is True
    assert looks_unindexed(raw_working_paper) is True

    result_monograph = classify([], raw_monograph)
    assert result_monograph.state == State.NOT_INDEXED
    assert result_monograph.state != State.GHOST
