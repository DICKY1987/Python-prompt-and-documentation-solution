#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
pip install -r SPEC/requirements.txt
pip install -r requirements-agentic.txt
echo "Bootstrap complete."
