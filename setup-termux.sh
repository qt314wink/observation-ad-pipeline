#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${1:-$HOME/Projects/observation-ad-pipeline-v2.1}"
pkg update -y
pkg upgrade -y
pkg install -y python git curl jq ffmpeg openssl coreutils unzip
mkdir -p "$ROOT"
SOURCE="$(pwd)"
if [ "$SOURCE" != "$ROOT" ]; then cp -a "$SOURCE"/. "$ROOT"/; fi
cd "$ROOT"
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
chmod +x bin/* scripts/* 2>/dev/null || true
cp -n .env.example .env || true
mkdir -p input/{images,videos,folders} output logs cache tmp tasks
printf '\nInstalled v2.1. Next:\n  cd %s\n  source .venv/bin/activate\n  obsad doctor\n  obsad new-task edit my-first-edit\n' "$ROOT"
