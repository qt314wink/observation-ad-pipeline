#!/usr/bin/env bash
set -euo pipefail

ROOT="${OBSAD_ROOT:-$(pwd)}"
CAMPAIGN="campaigns/calcium-nourish-the-signal"
EVIDENCE_DIR="${OBSAD_EVIDENCE_DIR:-.artifacts/calcium-execution-v1}"

log(){ printf '\n==> %s\n' "$*"; }
die(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }

cd "$ROOT"
test -f pyproject.toml || die "Run from observation-ad-pipeline repo root or set OBSAD_ROOT."

log "Repository state"
git status --short --branch
git log -1 --oneline

log "System dependencies"
if command -v apt-get >/dev/null 2>&1; then
  if [ "${INSTALL_SYSTEM_DEPS:-0}" = "1" ]; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip git curl jq ffmpeg
  fi
elif command -v pkg >/dev/null 2>&1; then
  if [ "${INSTALL_SYSTEM_DEPS:-0}" = "1" ]; then
    pkg update -y
    pkg install -y python git curl jq ffmpeg openssl coreutils
  fi
fi

for cmd in python git curl jq ffmpeg; do
  command -v "$cmd" >/dev/null 2>&1 || die "Missing required command: $cmd"
done

log "Python environment"
python - <<'PY'
import sys
print(sys.version)
if sys.version_info < (3,10):
    raise SystemExit("Python >=3.10 required; Python 3.12 preferred to match CI.")
PY

if [ ! -d .venv ]; then
  python -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e . pytest

log "Baseline doctor"
python -m obsad.cli doctor --url "${COMFY_URL:-http://127.0.0.1:8188}" || true

log "Campaign validation"
python -m obsad.cli campaign-validate "$CAMPAIGN"
pytest -q tests/test_campaign.py
PYTHONPATH=src python -m unittest discover -s tests -v
git diff --check

log "Deterministic anchor compilation"
mkdir -p "$EVIDENCE_DIR/compiled"
providers=(openai xai comfyui wan)
tasks=(K01 K04 K07 K08)

for provider in "${providers[@]}"; do
  for task in "${tasks[@]}"; do
    a="$EVIDENCE_DIR/compiled/${provider}-${task}-a.json"
    b="$EVIDENCE_DIR/compiled/${provider}-${task}-b.json"
    python -m obsad.cli campaign-compile "$CAMPAIGN" --provider "$provider" --task-id "$task" --out "$a" >/dev/null
    python -m obsad.cli campaign-compile "$CAMPAIGN" --provider "$provider" --task-id "$task" --out "$b" >/dev/null
    diff -u "$a" "$b" >/dev/null || die "Non-deterministic compile: $provider $task"
    sha256sum "$a"
  done
done

log "Credential/runtime capability probe (presence only)"
python - <<'PY'
import os, json
keys = ["OPENAI_API_KEY", "XAI_API_KEY", "COMFY_URL"]
print(json.dumps({k: bool(os.getenv(k)) for k in keys}, indent=2))
PY

if [ -n "${COMFY_URL:-}" ]; then
  log "Remote ComfyUI probe"
  curl -fsS --max-time 20 "${COMFY_URL%/}/system_stats" | jq . > "$EVIDENCE_DIR/comfy-system-stats.json" || {
    echo "ComfyUI endpoint not reachable; generation remains blocked." >&2
  }
fi

if [ "${INSTALL_COMFYUI:-0}" = "1" ]; then
  COMFYUI_ROOT="${COMFYUI_ROOT:-$HOME/ComfyUI}"
  if [ ! -d "$COMFYUI_ROOT/.git" ]; then
    log "Cloning official ComfyUI (no model weights)"
    git clone --depth 1 https://github.com/Comfy-Org/ComfyUI.git "$COMFYUI_ROOT"
  else
    log "Existing ComfyUI checkout found at $COMFYUI_ROOT"
  fi
  echo "No model weights were downloaded. Inspect campaign workflow requirements before installing any."
fi

log "OpenAI video warning"
cat <<'EOF'
As of 2026-09-20, OpenAI's official docs state that the Sora 2 Videos API is
deprecated and scheduled to shut down on 2026-09-24. Do not build a new Sora
execution path without re-verifying the current official docs.
EOF

log "Ready"
printf 'Evidence: %s\n' "$EVIDENCE_DIR"
printf 'Next: review compiled K01/K04/K07/K08 payloads, then execute only with authorized runtime/credentials.\n'
