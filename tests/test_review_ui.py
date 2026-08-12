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


def test_vercel_serves_review_as_static_root():
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    assert config["outputDirectory"] == "review"

