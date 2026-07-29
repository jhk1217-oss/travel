#!/usr/bin/env bash
# Real-Time-Voice-Cloning 원클릭 설치 스크립트 (Linux/macOS/WSL)
# 사용: bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "==> [1/5] uv 확인/설치"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
uv --version

echo "==> [2/5] ffmpeg 확인 (mp3/m4a 샘플 읽기에 필요)"
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "    ffmpeg가 없습니다. 설치를 권장합니다:"
  echo "      Ubuntu/WSL: sudo apt-get install -y ffmpeg"
  echo "      macOS:      brew install ffmpeg"
  echo "    (wav 샘플만 쓸 경우 없어도 동작)"
fi

mkdir -p my-voice output

echo "==> [3/5] Real-Time-Voice-Cloning 클론"
if [ ! -d Real-Time-Voice-Cloning ]; then
  git clone --depth 1 https://github.com/CorentinJ/Real-Time-Voice-Cloning.git
fi

echo "==> [4/5] 의존성 설치 (Python 3.9 + PyTorch CPU)"
cd Real-Time-Voice-Cloning
# visdom은 학습 시각화 전용인데 최신 setuptools에서 빌드가 깨지므로 제거(추론에 불필요)
sed -i.bak '/"visdom==0.1.8.9",/d' pyproject.toml && rm -f pyproject.toml.bak
# NVIDIA GPU + CUDA 11.x 환경이면 --extra cpu 대신 --extra cuda 사용 가능
uv sync --extra cpu

echo "==> [5/5] 사전학습 모델 다운로드 (~440MB, Hugging Face)"
uv run python -c "from pathlib import Path; from utils.default_models import ensure_default_models; ensure_default_models(Path('saved_models'))"

echo
echo "설치 완료! 사용법은 README.md 참고. 빠른 시작:"
echo "  ./narrate.sh --voice my-voice/내샘플.wav --text example-script.txt --out output/narration.wav"
