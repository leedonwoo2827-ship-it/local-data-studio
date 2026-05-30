#!/usr/bin/env bash
# Local Data Studio - macOS/Linux run
set -e
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source .venv/bin/activate
streamlit run app.py
