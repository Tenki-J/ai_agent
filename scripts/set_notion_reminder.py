"""
지스타 2026 입장권 예매 오픈 1주일 전 Notion 알람 설정
대상 페이지: 🎟️ 지스타 2026 입장권 예매 오픈 (예상)
날짜: 2026-10-15 → 리마인더: 1주 전 (2026-10-08)
"""
import os
import sys, io, requests, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION, "Content-Type": "application/json"}

PAGE_ID = "38663685-d218-8137-b5a0-feecd3aa421d"   # 🎟️ 지스타 2026 입장권 예매 오픈

# 현재 페이지 상태 확인
print("── 현재 페이지 날짜 속성 확인")
r = requests.get(f"{BASE}/pages/{PAGE_ID}", headers=H)
data = r.json()
date_prop = data.get("properties", {}).get("날짜", {})
print(f"  현재 날짜: {json.dumps(date_prop.get('date'), ensure_ascii=False)}")

# 날짜 속성에 reminder 설정 시도 (1주 전)
print("\n── 리마인더 설정 시도 (1주 전 = 2026-10-08)")
payload = {
    "properties": {
        "날짜": {
            "date": {
                "start": "2026-10-15",
                "reminder": {
                    "unit": "week",
                    "value": 1
                }
            }
        }
    }
}

r = requests.patch(f"{BASE}/pages/{PAGE_ID}", headers=H, json=payload)
print(f"  응답 코드: {r.status_code}")

if r.status_code == 200:
    result = r.json()
    date_after = result.get("properties", {}).get("날짜", {}).get("date", {})
    print(f"  설정 후 날짜 속성: {json.dumps(date_after, ensure_ascii=False, indent=2)}")
    print("\n[OK] 리마인더 설정 성공")
else:
    print(f"  오류 내용: {r.text[:500]}")
    print("\n[INFO] 날짜 속성 리마인더는 API 미지원 → 대안 방식 사용")
