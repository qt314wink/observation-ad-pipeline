import json
from pathlib import Path

from click.testing import CliRunner

from obsad.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/motion-references/magical-ai-books.yaml"


def test_motion_reference_validate_command_accepts_governed_fixture():
    runner = CliRunner()
    result = runner.invoke(main, ["motion-reference-validate", str(FIXTURE)])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "valid"


def test_motion_reference_render_is_deterministic_and_traceable(tmp_path):
    runner = CliRunner()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    result_a = runner.invoke(main, ["motion-reference-render", str(FIXTURE), "--out", str(first)])
    result_b = runner.invoke(main, ["motion-reference-render", str(FIXTURE), "--out", str(second)])
    assert result_a.exit_code == 0, result_a.output
    assert result_b.exit_code == 0, result_b.output
    assert first.read_bytes() == second.read_bytes()
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["referenceId"] == "video:reference:kelly-boesch:magical-ai-books"
    assert payload["canonicalDigest"].startswith("sha256:")
    assert len(payload["subjectContinuity"]) >= 1
    assert len(payload["scenes"]) == 10
