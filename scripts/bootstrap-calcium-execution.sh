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

for cmd in python3 git curl jq ffmpeg; do
  command -v "$cmd" >/dev/null 2>&1 || die "Missing required command: $cmd"
done

log "Python environment"
python3 - <<'PY'
import sys
print(sys.version)
if sys.version_info < (3,10):
    raise SystemExit("Python >=3.10 required; Python 3.12 preferred to match CI.")
PY

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e . pytest

log "Baseline doctor"
python3 -m obsad.cli doctor || true

log "Campaign validation"
python3 -m obsad.cli campaign-validate "$CAMPAIGN"
# Fixtures expect unresolved model placeholders. Keep configured models intact
# in the parent environment for the later execution-time compilation.
baseline_test() {
  env -u OBSAD_OPENAI_MODEL -u OBSAD_XAI_MODEL -u OBSAD_COMFY_CHECKPOINT -u OBSAD_WAN_MODEL "$@"
}
baseline_test python3 -m pytest -q tests/test_campaign.py
baseline_test env PYTHONPATH=src python3 -m unittest discover -s tests -v
git diff --check

log "Deterministic anchor compilation"
mkdir -p "$EVIDENCE_DIR/compiled"
providers=(openai xai comfyui wan)
tasks=(K01 K04 K07 K08)

for provider in "${providers[@]}"; do
  for task in "${tasks[@]}"; do
    a="$EVIDENCE_DIR/compiled/${provider}-${task}-a.json"
    b="$EVIDENCE_DIR/compiled/${provider}-${task}-b.json"
    python3 -m obsad.cli campaign-compile "$CAMPAIGN" --provider "$provider" --task-id "$task" --out "$a" >/dev/null
    python3 -m obsad.cli campaign-compile "$CAMPAIGN" --provider "$provider" --task-id "$task" --out "$b" >/dev/null
    diff -u "$a" "$b" >/dev/null || die "Non-deterministic compile: $provider $task"
    sha256sum "$a"
  done
done

log "Credential/runtime capability probe (presence only)"
python3 - <<'PY'
import os, json
keys = ["OPENAI_API_KEY", "XAI_API_KEY", "COMFY_URL"]
print(json.dumps({k: bool(os.getenv(k)) for k in keys}, indent=2))
PY

if [ -n "${COMFY_URL:-}" ]; then
  log "Remote ComfyUI probe"
  # Avoid putting the URL on the process command line or emitting HTTP errors.
  # The Python process reads it from its environment and reports no exception text.
  python3 - "$EVIDENCE_DIR/comfy-system-stats.json" <<'PY' || {
import json, os, sys
import requests
try:
    response = requests.get(os.environ['COMFY_URL'].rstrip('/') + '/system_stats', timeout=20)
    response.raise_for_status()
    data = response.json()
    with open(sys.argv[1], 'w', encoding='utf-8') as output:
        json.dump(data, output, indent=2)
        output.write('\n')
except Exception:
    sys.exit(1)
PY
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
