"""
지스타 2026 입장권 예매 오픈 일주일 전(2026-10-08) Notion 알람 설정
방법: 페이지 본문에 날짜 멘션 블록 추가 (Notion API가 지원하는 방식)

Notion API는 date property에 reminder 직접 설정 불가(400 에러).
대신 페이지 content에 date mention + 시간 지정 → Notion 앱에서 알람 수신 가능.
"""
import os
import sys, io, requests, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION, "Content-Type": "application/json"}

PAGE_ID = "38663685-d218-8137-b5a0-feecd3aa421d"   # 🎟️ 지스타 2026 입장권 예매 오픈

# 리마인더 날짜: 예매 오픈(10-15) 1주 전 = 10-08, 오전 9시
REMIND_DATE = "2026-10-08T09:00:00+09:00"  # KST
REMIND_PLAIN = "2026년 10월 8일 오전 9:00"

# ── 페이지 제목에 알람 표시 추가 ──────────────────────────
print("── 페이지 제목에 알람 표시 추가")
r = requests.patch(f"{BASE}/pages/{PAGE_ID}", headers=H, json={
    "properties": {
        "일정 제목": {
            "title": [{"type": "text", "text": {
                "content": "🎟️ 지스타 2026 입장권 예매 오픈 (예상) 🔔"
            }}]
        }
    }
})
print(f"  응답: {r.status_code}")

# ── 기존 블록 확인 ────────────────────────────────────────
print("\n── 기존 블록 수 확인")
r = requests.get(f"{BASE}/blocks/{PAGE_ID}/children", headers=H)
existing = r.json().get("results", [])
print(f"  기존 블록: {len(existing)}개")

# ── 알람 블록 추가 ────────────────────────────────────────
print("\n── 알람 블록 추가")

alarm_blocks = [
    # 구분선
    {"object": "block", "type": "divider", "divider": {}},

    # 알람 안내 callout
    {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {"type": "text", "text": {"content": "⏰ 알람 설정: "},
                 "annotations": {"bold": True}},
                # 날짜 멘션 (시간 포함) — Notion 앱에서 클릭 후 "Remind me" 설정 가능
                {
                    "type": "mention",
                    "mention": {
                        "type": "date",
                        "date": {
                            "start": REMIND_DATE,
                            "end": None
                        }
                    },
                    "plain_text": REMIND_PLAIN,
                    "annotations": {"bold": True, "color": "red"}
                },
                {"type": "text", "text": {"content": " — 예매 오픈 1주일 전 알람"}}
            ],
            "icon": {"type": "emoji", "emoji": "🔔"},
            "color": "yellow_background"
        }
    },

    # Notion UI 설정 안내
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {"type": "text", "text": {
                    "content": "Notion 앱에서 위 날짜를 클릭 → [Remind me] 선택 → 알람 시간 지정"
                }}
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {"type": "text", "text": {
                    "content": "모바일: 날짜 멘션 탭 → Remind → On date (당일 알람) 또는 원하는 시간 선택"
                }}
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {"type": "text", "text": {
                    "content": "데스크탑: 날짜 클릭 → 달력 팝업 → Remind 옵션 설정"
                }}
            ]
        }
    },

    # 예매 일정 요약
    {"object": "block", "type": "divider", "divider": {}},
    {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {"type": "text", "text": {
                    "content": "📌 예매 핵심 일정\n"
                              "• 알람 날짜: 2026년 10월 8일 (목) 오전 9시\n"
                              "• 예매 오픈: 2026년 10월 15일 (목) 오후 3시 (예상)\n"
                              "• 판매처: 예스24 단독 (예상)\n"
                              "• 100% 온라인 예매만 가능 / 현장 구매 불가"
                }}
            ],
            "icon": {"type": "emoji", "emoji": "📌"},
            "color": "blue_background"
        }
    },
]

r = requests.patch(f"{BASE}/blocks/{PAGE_ID}/children", headers=H, json={"children": alarm_blocks})
print(f"  응답: {r.status_code}")

if r.status_code == 200:
    added = r.json().get("results", [])
    print(f"  추가된 블록: {len(added)}개")
    print("\n[OK] 알람 블록 추가 완료")

    # 날짜 멘션 블록 ID 확인
    for b in added:
        if b.get("type") == "callout":
            content = b.get("callout", {}).get("rich_text", [])
            for rt in content:
                if rt.get("type") == "mention":
                    mention_date = rt.get("mention", {}).get("date", {})
                    print(f"\n  날짜 멘션 확인:")
                    print(f"    start: {mention_date.get('start')}")
                    print(f"    블록 ID: {b.get('id')}")
            break
else:
    print(f"  오류: {r.text[:300]}")
