#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "${OBSAD_ROOT:-$HOME/Projects/observation-ad-pipeline-v2}"
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade -r requirements.txt
python -m pip check
obsad doctor || true
