#!/usr/bin/env bash
# Local Data Studio - macOS/Linux setup
set -e
cd "$(dirname "$0")"

echo "[1/3] Creating virtual environment (.venv)..."
[ -d ".venv" ] || python3 -m venv .venv

echo "[2/3] Activating and upgrading pip..."
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip

echo "[3/3] Installing dependencies..."
pip install -r requirements.txt

echo
echo "Done. Next:"
echo "  1) cp .env.example .env  &&  edit UBION_LITELLM_KEY"
echo "  2) ./run.sh"
