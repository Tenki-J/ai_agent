"""
Typecast TTS API 연동 스크립트
Usage: python scripts/typecast_tts.py "텍스트" [출력파일명.wav]
"""

import sys
import os
import requests

API_KEY = "__pltSzc6Y22jfjdbmwwSV3NzLAz6WbhMwiTuwqas69JF"
VOICE_ID = "tc_699d27c4b4af39da12bfff46"
API_URL = "https://api.typecast.ai/v1/text-to-speech"


def synthesize(text: str, output_path: str = "output.wav") -> bool:
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "voice_id": VOICE_ID,
        "text": text,
        "model": "ssfm-v30",
        "language": "kor",
        "output": {
            "volume": 100,
            "audio_pitch": 0,
            "audio_tempo": 1,
            "audio_format": "wav",
        },
    }

    print(f"[TTS] 텍스트: {text}")
    print(f"[TTS] Voice ID: {VOICE_ID}")

    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        size_kb = len(response.content) / 1024
        print(f"[TTS] 완료: {output_path} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"[TTS] 오류 {response.status_code}: {response.text}")
        return False


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "안녕하세요."
    output = sys.argv[2] if len(sys.argv) > 2 else "results/tts_output.wav"

    os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
    success = synthesize(text, output)
    sys.exit(0 if success else 1)
