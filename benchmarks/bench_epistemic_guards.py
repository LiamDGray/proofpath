"""Benchmark demonstrating elimination of epistemic defects (D1, D2, D3).

Compares audit outputs before and after epistemic guards on real-world reference types:
- D1: /doi/abs/ publisher landing page classification
- D2: False REFUTED contradiction prevention on abstracts
- D3: False GHOST REFERENCE elimination on non-indexed academic documents
"""

from proofpath.config import Config
from proofpath.document import Claim, Locator, Reference
from proofpath.fetch import Fetcher, _Response
from proofpath.models import Label, Passage, Verdict
from proofpath.report import Kind, SourceStatus
from proofpath.resolve import State, classify, looks_unindexed
from proofpath.verify import _verdict_finding


def run_benchmark():
    print("Running Proofpath Epistemic Guards Benchmark...")
    print("=" * 70)

    # 1. D1 Guard Test: Landing pages must not be fulltext
    fetcher = Fetcher(config=Config())
    resp = _Response(
        status=200,
        content_type="text/html",
        body=b"<html><body>Abstract only text...</body></html>",
        final_url="https://journals.sagepub.com/doi/abs/10.1177/0001",
    )
    fetched = fetcher._finish("https://journals.sagepub.com/doi/abs/10.1177/0001", 1, resp, "fulltext", [])
    d1_passed = fetched.text_kind == "landing"
    print(f"D1 Guard (Landing Page Detection):      {'PASS' if d1_passed else 'FAIL'} (text_kind={fetched.text_kind})")

    # 2. D2 Guard Test: Refusal of contradictions from abstracts
    claim = Claim(
        paragraph=1,
        sentence=1,
        locator=Locator(line=1, column=1, page=1),
        text="Sample claim about sociology.",
        cited_refs=(1,),
    )
    ref = Reference(number=1, locator=Locator(line=10, column=1, page=1), raw="Author 2020.")
    verdict = Verdict(
        label=Label.REFUTED,
        score=0.9,
        passage=Passage(text="Contradicting snippet in abstract", source_id="doi:1", index=0),
        reason="contradiction",
        tier="high",
    )
    status_abstract = SourceStatus(
        reference=ref,
        resolve=None,
        retraction=None,
        source_id="doi:1",
        text_kind="abstract",
        state="",
        fetch_step=1,
        url="https://doi.org/1",
        from_cache=False,
    )
    finding = _verdict_finding(claim, status_abstract, verdict)
    d2_passed = finding is not None and finding.kind == Kind.NEI
    print(f"D2 Guard (Abstract Refutation Demotion): {'PASS' if d2_passed else 'FAIL'} (verdict={finding.kind.value})")

    # 3. D3 Guard Test: Unindexed monographs/theses not called GHOST
    unindexed_citations = [
        "Arendt, H. 1951. The Origins of Totalitarianism. Monograph series.",
        "Author, A. 2018. Epistemic Humility in Practice. PhD thesis.",
        "Researcher, B. 2021. LLM Evaluation Flaws. Working paper 102.",
    ]
    d3_passed = True
    for cit in unindexed_citations:
        res = classify([], cit)
        if res.state == State.GHOST:
            d3_passed = False
            break
    print(f"D3 Guard (Monograph/Thesis Ghost Guard):  {'PASS' if d3_passed else 'FAIL'} (state={res.state.value})")

    print("=" * 70)
    assert d1_passed and d2_passed and d3_passed
    print("Epistemic Guards Verdict: ALL 3 GUARDS OPERATIONAL.")


if __name__ == "__main__":
    run_benchmark()
