#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

mkdir -p data/known_faces data/unknown_faces data/conversation_cache
echo "Entorno PC listo."
