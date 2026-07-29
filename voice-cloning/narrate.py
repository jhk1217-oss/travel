#!/usr/bin/env python
"""
narrate.py — 내 목소리로 영어 나레이션 생성 (Real-Time-Voice-Cloning 기반)

사용 예:
    ./narrate.sh --voice my-voice/sample.wav --text example-script.txt --out output/narration.wav

옵션:
    --voice  목소리 샘플 파일(wav/mp3/m4a/flac). 여러 개 주면 임베딩을 평균해서 더 안정적.
    --text   나레이션 대본 텍스트 파일(영어). 문장 단위(. ! ?)로 잘라 합성한다.
    --out    출력 WAV 경로 (기본: output/narration.wav)
    --pause  문장 사이 무음 초 (기본 0.35)
    --seed   랜덤 시드(같은 시드 = 같은 결과)

주의: 합성기가 영어 데이터로만 학습되어 있어 대본은 반드시 영어여야 한다.
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RTVC = HERE / "Real-Time-Voice-Cloning"
sys.path.insert(0, str(RTVC))

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import torch  # noqa: E402

from encoder import inference as encoder  # noqa: E402
from synthesizer.inference import Synthesizer  # noqa: E402
from utils.default_models import ensure_default_models  # noqa: E402
from vocoder import inference as vocoder  # noqa: E402


def split_sentences(text: str) -> list:
    """문장 단위로 분리. 25단어가 넘는 문장은 쉼표에서 한 번 더 자른다."""
    text = re.sub(r"\s+", " ", text).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    chunks = []
    for s in sentences:
        if len(s.split()) <= 25:
            chunks.append(s)
            continue
        part = []
        for token in s.split(", "):
            part.append(token)
            if len(" ".join(part).split()) >= 15:
                chunks.append(", ".join(part).rstrip(",") + ",")
                part = []
        if part:
            chunks.append(", ".join(part))
    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--voice", type=Path, nargs="+", required=True, help="voice sample file(s)")
    parser.add_argument("--text", type=Path, required=True, help="English script text file")
    parser.add_argument("--out", type=Path, default=HERE / "output" / "narration.wav")
    parser.add_argument("--pause", type=float, default=0.35, help="silence between sentences (s)")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    for f in args.voice:
        if not f.exists():
            sys.exit(f"목소리 샘플을 찾을 수 없음: {f}")
    if not args.text.exists():
        sys.exit(f"대본 파일을 찾을 수 없음: {args.text}")

    text = args.text.read_text(encoding="utf-8")
    if re.search(r"[가-힣]", text):
        sys.exit("대본에 한글이 포함되어 있습니다. 이 모델은 영어 전용입니다. "
                 "(한국어 나레이션은 README의 '한국어 나레이션이 필요하다면' 참고)")

    chunks = split_sentences(text)
    if not chunks:
        sys.exit("대본이 비어 있습니다.")
    print(f"대본 {len(chunks)}개 문장으로 분리 완료")

    if args.seed is not None:
        torch.manual_seed(args.seed)

    print("모델 로딩 중...")
    ensure_default_models(RTVC / "saved_models")
    encoder.load_model(RTVC / "saved_models" / "default" / "encoder.pt")
    synthesizer = Synthesizer(RTVC / "saved_models" / "default" / "synthesizer.pt")
    vocoder.load_model(RTVC / "saved_models" / "default" / "vocoder.pt")

    print("목소리 임베딩 계산 중...")
    embeds = []
    for f in args.voice:
        wav = encoder.preprocess_wav(f)
        if len(wav) < encoder.sampling_rate:
            print(f"  경고: {f.name} 은 유효 음성이 1초 미만 — 더 긴 샘플 권장")
        embeds.append(encoder.embed_utterance(wav))
    embed = np.mean(embeds, axis=0)
    embed /= np.linalg.norm(embed)

    print("문장 합성 중...")
    specs = synthesizer.synthesize_spectrograms(chunks, [embed] * len(chunks))

    sr = synthesizer.sample_rate
    silence = np.zeros(int(args.pause * sr), dtype=np.float32)
    pieces = []
    for i, spec in enumerate(specs):
        print(f"  [{i + 1}/{len(specs)}] {chunks[i][:60]}")
        wav = vocoder.infer_waveform(spec)
        print()  # vocoder progress bar doesn't end with newline
        wav = np.pad(wav, (0, sr // 4), mode="constant")
        wav = encoder.preprocess_wav(wav)  # trim silences (RTVC issue #53)
        pieces.append(wav.astype(np.float32))
        pieces.append(silence)

    result = np.concatenate(pieces[:-1])
    result /= max(1e-8, np.abs(result).max())  # normalize to avoid clipping
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(args.out), result, sr)
    print(f"\n완료: {args.out} ({len(result) / sr:.1f}초)")


if __name__ == "__main__":
    main()
