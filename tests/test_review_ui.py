import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_review_ui_is_static_accessible_and_data_backed():
    html = (ROOT / "review/index.html").read_text(encoding="utf-8")
    assert '<main id="main-content">' in html
    assert 'aria-live="polite"' in html
    assert 'data/mandala-reel-set.json' in (ROOT / "review/app.js").read_text(encoding="utf-8")
    data = json.loads((ROOT / "review/data/mandala-reel-set.json").read_text(encoding="utf-8"))
    assert len(data["sources"]) == 4
    assert all(source["evidenceStatus"] == "pending-source-verification" for source in data["sources"])


def test_motion_reference_workbench_has_two_corpora_and_fast_read_sections():
    html = (ROOT / "review/index.html").read_text(encoding="utf-8")
    app = (ROOT / "review/app.js").read_text(encoding="utf-8")
    index_path = ROOT / "review/data/index.json"
    magical_path = ROOT / "review/data/magical-ai-books.json"
    assert index_path.exists(), "workbench must expose a corpus index"
    assert magical_path.exists(), "workbench must expose derived Magical AI Books review data"
    corpus_index = json.loads(index_path.read_text(encoding="utf-8"))
    assert {item["id"] for item in corpus_index["datasets"]} == {"mandala-reel-set", "magical-ai-books"}
    assert "data/index.json" in app
    for heading in ("Movement quality", "Director controls", "What we think", "What remains uncertain"):
        assert heading in html


def test_magical_ai_books_review_payload_is_traceable_and_read_only():
    payload_path = ROOT / "review/data/magical-ai-books.json"
    assert payload_path.exists()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert payload["referenceId"] == "video:reference:kelly-boesch:magical-ai-books"
    assert payload["canonicalDigest"].startswith("sha256:")
    assert len(payload["scenes"]) == 10
    assert payload["experimentGate"]["status"] == "blocked"
    assert payload["candidatePrimitives"][0]["status"] == "candidate"
    assert all("question" in control and "whatYouWillSee" in control for control in payload["directorControls"])


def test_vercel_serves_review_as_static_root():
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    assert config["outputDirectory"] == "review"
