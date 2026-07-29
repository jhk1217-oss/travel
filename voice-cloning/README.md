# 목소리 복제 나레이션 (Real-Time-Voice-Cloning)

[CorentinJ/Real-Time-Voice-Cloning](https://github.com/CorentinJ/Real-Time-Voice-Cloning)(SV2TTS)으로
**내 목소리 샘플 몇 초만으로** 그 목소리의 나레이션 음성을 만드는 설정입니다.

> ⚠️ **가장 중요한 한계: 이 모델은 영어 전용입니다.**
> 합성기가 영어 데이터(LibriSpeech)로만 학습되어 있어 **영어 대본만** 나레이션할 수 있습니다.
> 한국어 대본을 넣으면 알아들을 수 없는 소리가 나옵니다. 한국어 나레이션이 목표라면
> 아래 [한국어 나레이션이 필요하다면](#한국어-나레이션이-필요하다면) 섹션을 먼저 보세요.

---

## 1. 설치 (최초 1회)

Linux / macOS / WSL(Windows는 WSL 권장):

```bash
cd voice-cloning
bash setup.sh
```

스크립트가 하는 일: ① [uv](https://docs.astral.sh/uv/) 설치 → ② 원본 저장소 클론 →
③ Python 3.9 가상환경 + PyTorch(CPU) 설치 → ④ 사전학습 모델 3개(~440MB) 다운로드.
디스크 약 3GB, GPU 불필요(CPU로 동작, GPU 있으면 `setup.sh` 주석 참고).

## 2. 내 목소리 샘플 준비

1. **조용한 곳**에서 자연스러운 톤으로 아무 문장이나 읽어 녹음 (영어 낭독이면 더 좋음)
2. 길이 **5초 ~ 1분** (너무 짧으면 품질 저하), 형식은 wav/mp3/m4a/flac 아무거나
3. `voice-cloning/my-voice/` 폴더에 저장 (이 폴더는 git에 올라가지 않음)

샘플을 2~3개 녹음해서 모두 넘기면 임베딩을 평균해 더 안정적인 결과가 나옵니다.

## 3. 나레이션 생성

영어 대본을 텍스트 파일로 저장한 뒤:

```bash
./narrate.sh --voice my-voice/sample1.wav my-voice/sample2.wav \
             --text example-script.txt \
             --out output/narration.wav
```

- 대본은 문장 단위로 잘라 합성합니다. **한 문장 20단어 내외**가 품질이 가장 좋습니다.
- `--pause 0.5` 로 문장 사이 간격 조절, `--seed 42` 로 결과 고정 가능.
- CPU 기준 오디오 1초 생성에 약 2초 걸립니다.

### GUI 툴박스 (선택)

로컬 데스크톱에서는 원본의 GUI로 실시간 실험도 가능합니다:

```bash
cd Real-Time-Voice-Cloning
uv run python demo_toolbox.py
```

## 4. 품질에 대한 기대치

이 프로젝트는 2019년 논문 데모입니다. 목소리의 **톤·음색은 따라오지만** 음질은 16kHz로
다소 뭉툭하고, 억양이 어색한 문장도 나옵니다. 문장을 짧게 쓰고, 시드를 바꿔가며
여러 번 생성해 좋은 테이크를 고르는 방식을 추천합니다.

## 한국어 나레이션이 필요하다면

이 저장소(여행 루트 가이드)의 나레이션은 한국어일 가능성이 높은데, RTVC로는 불가능합니다.
한국어를 지원하는 목소리 복제 대안:

| 도구 | 한국어 | 비용/라이선스 | 비고 |
|---|---|---|---|
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | ✅ | 무료(MIT) | 1분 샘플로 고품질, 한국어 공식 지원. 현재 오픈소스 중 최선 |
| [Coqui XTTS-v2](https://huggingface.co/coqui/XTTS-v2) | ✅ | 무료(비상업 CPML) | 6초 샘플 제로샷. 상업(유튜브 수익화 등) 사용 불가에 주의 |
| ElevenLabs / Typecast 등 상용 서비스 | ✅ | 유료 | 품질 최상, 설치 불필요 |

유튜브 수익화 영상에 쓸 거라면 **GPT-SoVITS(MIT)** 또는 상용 서비스를 권장합니다.

## 주의사항 (윤리·법적)

**본인 목소리** 또는 명시적으로 동의한 사람의 목소리만 복제하세요.
타인 목소리 무단 복제는 법적 문제(퍼블리시티권·성명권 침해 등)가 될 수 있습니다.
원본 프로젝트 라이선스: MIT (단, 학습 데이터셋 LibriSpeech는 비상업 연구용 —
생성물의 상업적 이용 전 원본 저장소의 안내를 확인하세요).

## 폴더 구조

```
voice-cloning/
├── setup.sh                  # 원클릭 설치
├── narrate.sh                # 나레이션 생성 실행 래퍼
├── narrate.py                # 나레이션 생성 스크립트 (대본 → WAV)
├── example-script.txt        # 영어 대본 예시
├── my-voice/                 # 내 목소리 샘플 (git 제외)
├── output/                   # 생성된 나레이션 (git 제외)
└── Real-Time-Voice-Cloning/  # 원본 저장소 클론 (git 제외, setup.sh가 생성)
```
