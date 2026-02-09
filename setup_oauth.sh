#!/usr/bin/env bash
set -euo pipefail

# Creates virtualenv, installs requirements, and runs OAuth setup helper
# Usage: ./setup_oauth.sh

if [ ! -f requirements.txt ]; then
  echo "requirements.txt not found in $(pwd)"
  exit 1
fi

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python oauth_setup.py

echo "OAuth setup complete. token.json saved in this folder."
