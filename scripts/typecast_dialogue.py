"""
뽀또 & 억울이 대화 TTS 생성 스크립트
각 대사를 개별 WAV로 생성 후 MP3 하나로 합침
"""

import os
import time
import requests
import static_ffmpeg
static_ffmpeg.add_paths()

from pydub import AudioSegment

API_KEY = "__pltSzc6Y22jfjdbmwwSV3NzLAz6WbhMwiTuwqas69JF"
API_URL = "https://api.typecast.ai/v1/text-to-speech"

VOICES = {
    "뽀또": "tc_699d27c4b4af39da12bfff46",
    "억울이": "tc_699d27ef573c4c4d91aa411d",
}

# 약 1분 분량의 대화 (뽀또 = 기다리던 쪽, 억울이 = 10분 늦은 쪽)
DIALOGUE = [
    ("뽀또",  "야, 억울이! 10분이나 늦었잖아. 연락도 없이!"),
    ("억울이", "미안미안! 근데 진짜 어쩔 수 없었어. 내 말 좀 들어봐."),
    ("뽀또",  "무슨 일인데? 또 무슨 핑계야?"),
    ("억울이", "핑계가 아니라고! 횡단보도 건너려는데 갑자기 고양이 한 마리가 쓰러진 거야!"),
    ("뽀또",  "에? 고양이가? 진짜?"),
    ("억울이", "응! 그냥 지나칠 수가 없잖아. 옆에 앉아서 괜찮은지 확인하고, 지나가는 사람한테 도움도 요청하고... 그러다 보니까 10분이 순식간에 지나간 거야."),
    ("뽀또",  "아... 그래서 연락도 못 한 거구나."),
    ("억울이", "핸드폰 꺼낼 틈도 없었다고! 나도 빨리 오고 싶었어. 진짜 억울하지 않아? 착한 일 하다가 늦었는데 혼날 것 같잖아."),
    ("뽀또",  "야... 사실 혼내려고 했는데. 그건 진짜 어쩔 수 없었겠다."),
    ("억울이", "그치? 나 억울하지?"),
    ("뽀또",  "억울하긴 한데... 그나저나 그 고양이는 괜찮았어?"),
    ("억울이", "응, 다행히 곧 일어났어. 그거 확인하고 바로 달려온 거야!"),
    ("뽀또",  "그래, 잘했어. 근데 다음엔 연락이라도 해줘!"),
    ("억울이", "알겠어, 미안~ 오늘은 내가 살게!"),
    ("뽀또",  "그래, 그 정도는 해야지. 가자!"),
]

SILENCE_BETWEEN = 400  # 대사 사이 묵음 (ms)


def synthesize_wav(text: str, voice_name: str, path: str) -> bool:
    voice_id = VOICES[voice_name]
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    payload = {
        "voice_id": voice_id,
        "text": text,
        "model": "ssfm-v30",
        "language": "kor",
        "output": {"volume": 100, "audio_pitch": 0, "audio_tempo": 1, "audio_format": "wav"},
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code == 200:
        with open(path, "wb") as f:
            f.write(resp.content)
        print(f"  [{voice_name}] {text[:20]}... → {os.path.basename(path)}")
        return True
    else:
        print(f"  오류 {resp.status_code}: {resp.text}")
        return False


def main():
    tmp_dir = "results/dialogue_tmp"
    os.makedirs(tmp_dir, exist_ok=True)

    segments = []
    silence = AudioSegment.silent(duration=SILENCE_BETWEEN)

    print("=== 대사 TTS 생성 중 ===")
    for i, (speaker, text) in enumerate(DIALOGUE):
        wav_path = os.path.join(tmp_dir, f"{i:02d}_{speaker}.wav")
        ok = synthesize_wav(text, speaker, wav_path)
        if not ok:
            print(f"  {i}번 대사 실패, 건너뜀")
            continue
        seg = AudioSegment.from_wav(wav_path)
        segments.append(seg)
        segments.append(silence)
        time.sleep(0.3)  # API rate limit 방지

    print("\n=== 합치는 중 ===")
    combined = segments[0]
    for seg in segments[1:]:
        combined += seg

    out_path = "results/뽀또_억울이_대화.mp3"
    combined.export(out_path, format="mp3", bitrate="192k")
    duration_sec = len(combined) / 1000
    print(f"\n완료: {out_path}")
    print(f"총 길이: {duration_sec:.1f}초 ({len(combined)/1000/60:.1f}분)")
    return out_path


def send_email(mp3_path: str):
    import subprocess

    npm_bin = os.path.join(os.environ.get("APPDATA", ""), "npm")
    env = os.environ.copy()
    env["PATH"] = npm_bin + ";" + env.get("PATH", "")

    cmd = [
        "powershell", "-Command",
        f'$env:PATH = "{npm_bin};" + $env:PATH; '
        f'gws gmail "+send" --to "shoo_white@naver.com" '
        f'--subject "뽀또와 억울이의 대화 MP3" '
        f'--body "타입캐스트 TTS로 생성한 뽀또와 억울이의 대화 음성 파일입니다.`n`n줄거리: 억울이가 횡단보도에서 쓰러진 고양이를 도와주느라 약속에 10분 늦은 이야기" '
        f'-a "{os.path.abspath(mp3_path)}"',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        print(f"\n[메일] shoo_white@naver.com 으로 발송 완료!")
        print(result.stdout)
    else:
        print(f"\n[메일] 발송 실패: {result.stderr}")


if __name__ == "__main__":
    mp3 = main()
    if mp3:
        send_email(mp3)
