# typecast-tts

Typecast TTS API를 사용해 텍스트를 음성(WAV)으로 변환하는 스킬.

## Trigger

사용자가 다음과 같은 표현을 쓸 때 이 스킬을 사용한다:
- "TTS로 읽어줘", "음성으로 변환해줘", "타입캐스트로 말해줘"
- "뽀또 목소리로 ~", "음성 파일 만들어줘"
- "typecast TTS", "/tts"

## Configuration

| 항목 | 값 |
|------|-----|
| API Key | `__pltSzc6Y22jfjdbmwwSV3NzLAz6WbhMwiTuwqas69JF` |
| Voice ID (뽀또) | `tc_699d27c4b4af39da12bfff46` |
| Endpoint | `POST https://api.typecast.ai/v1/text-to-speech` |
| Model | `ssfm-v30` |
| Language | `kor` |
| Output format | `wav` |

## Usage

```bash
python scripts/typecast_tts.py "변환할 텍스트" [출력경로.wav]
```

출력 경로 생략 시 `results/tts_output.wav`에 저장된다.

## Steps

1. 사용자로부터 변환할 텍스트를 받는다.
2. `scripts/typecast_tts.py`를 실행한다.
3. 생성된 WAV 파일 경로와 크기를 사용자에게 알려준다.
4. 필요 시 파일을 재생하거나 커밋·푸시한다.

## API Reference

- **Endpoint**: `POST https://api.typecast.ai/v1/text-to-speech`
- **Auth Header**: `X-API-KEY: <api-key>`
- **Request Body**:
  ```json
  {
    "voice_id": "tc_699d27c4b4af39da12bfff46",
    "text": "안녕하세요.",
    "model": "ssfm-v30",
    "language": "kor",
    "output": {
      "volume": 100,
      "audio_pitch": 0,
      "audio_tempo": 1,
      "audio_format": "wav"
    }
  }
  ```
- **Response**: 바이너리 WAV 오디오 데이터 (200 OK)
