#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  ffmpeg \
  espeak-ng \
  portaudio19-dev \
  libatlas-base-dev \
  playerctl \
  build-essential \
  cmake \
  libopenblas-dev \
  liblapack-dev \
  libjpeg-dev \
  libtiff5-dev \
  libopenjp2-7-dev \
  libpng-dev \
  libavcodec-dev \
  libavformat-dev \
  libswscale-dev \
  libgtk2.0-dev \
  libcanberra-gtk-module \
  libxvidcore-dev \
  libx264-dev \
  libgtk-3-dev \
  libv4l-dev \
  libdc1394-dev \
  libxml2-dev \
  libxslt1-dev

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

mkdir -p data/known_faces data/unknown_faces data/conversation_cache
echo "Entorno Raspberry Pi listo."
