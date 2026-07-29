#!/usr/bin/env bash
# narrate.py를 Real-Time-Voice-Cloning의 가상환경으로 실행하는 래퍼
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$DIR/Real-Time-Voice-Cloning/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "가상환경이 없습니다. 먼저 실행하세요: bash $DIR/setup.sh" >&2
  exit 1
fi
exec "$PY" "$DIR/narrate.py" "$@"
