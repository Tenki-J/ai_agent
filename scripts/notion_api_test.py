"""
Notion API 접근 테스트 스크립트
- 연결 확인 (봇 정보 조회)
- 검색 (접근 가능한 페이지/DB 목록)
- 페이지 읽기
- 페이지 생성
- 페이지 업데이트
"""

import os
import sys
import io
import requests
import json
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

BASE_URL = "https://api.notion.com/v1"


def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def ok(msg):
    print(f"  [OK] {msg}")


def fail(msg):
    print(f"  [FAIL] {msg}")


def info(msg):
    print(f"  {msg}")


# ── 1. 연결 확인 ──────────────────────────────────────────
section("1. 연결 확인 — 봇(Integration) 정보 조회")
r = requests.get(f"{BASE_URL}/users/me", headers=HEADERS)
if r.status_code == 200:
    data = r.json()
    ok(f"연결 성공")
    info(f"Bot 이름  : {data.get('name', 'N/A')}")
    info(f"Bot ID    : {data.get('id', 'N/A')}")
    info(f"타입      : {data.get('type', 'N/A')}")
else:
    fail(f"연결 실패 — {r.status_code}: {r.text}")


# ── 2. 검색 — 접근 가능한 페이지/DB 목록 ─────────────────
section("2. 검색 — 접근 가능한 페이지 · 데이터베이스")
r = requests.post(
    f"{BASE_URL}/search",
    headers=HEADERS,
    json={"page_size": 10},
)
accessible_pages = []
accessible_dbs = []

if r.status_code == 200:
    results = r.json().get("results", [])
    ok(f"검색 성공 — 총 {len(results)}개 항목 접근 가능")
    for item in results:
        otype = item.get("object")
        oid = item.get("id")
        if otype == "page":
            # 타이틀 추출
            props = item.get("properties", {})
            title_val = ""
            for v in props.values():
                if v.get("type") == "title":
                    arr = v.get("title", [])
                    title_val = "".join(t.get("plain_text", "") for t in arr)
                    break
            if not title_val:
                title_val = "(제목 없음)"
            info(f"  [PAGE] {title_val[:40]} | id={oid}")
            accessible_pages.append(oid)
        elif otype == "database":
            title_arr = item.get("title", [])
            db_title = "".join(t.get("plain_text", "") for t in title_arr)
            if not db_title:
                db_title = "(제목 없음)"
            info(f"  [DB  ] {db_title[:40]} | id={oid}")
            accessible_dbs.append(oid)
else:
    fail(f"검색 실패 — {r.status_code}: {r.text}")


# ── 3. 페이지 읽기 ────────────────────────────────────────
section("3. 페이지 읽기 — 첫 번째 접근 가능한 페이지")
if accessible_pages:
    pid = accessible_pages[0]
    r = requests.get(f"{BASE_URL}/pages/{pid}", headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        ok(f"페이지 읽기 성공 (id={pid})")
        props = data.get("properties", {})
        for k, v in list(props.items())[:5]:
            vtype = v.get("type", "")
            if vtype == "title":
                val = "".join(t.get("plain_text", "") for t in v.get("title", []))
                info(f"  {k}: {val}")
            elif vtype == "rich_text":
                val = "".join(t.get("plain_text", "") for t in v.get("rich_text", []))
                info(f"  {k}: {val[:60]}")
            else:
                info(f"  {k}: ({vtype})")
    else:
        fail(f"페이지 읽기 실패 — {r.status_code}: {r.text}")
else:
    info("접근 가능한 페이지가 없어 읽기 테스트를 건너뜁니다.")


# ── 4. 블록(본문) 읽기 ────────────────────────────────────
section("4. 블록(본문) 읽기 — 첫 번째 페이지 블록 조회")
if accessible_pages:
    pid = accessible_pages[0]
    r = requests.get(f"{BASE_URL}/blocks/{pid}/children?page_size=5", headers=HEADERS)
    if r.status_code == 200:
        blocks = r.json().get("results", [])
        ok(f"블록 읽기 성공 — {len(blocks)}개 블록")
        for b in blocks:
            btype = b.get("type", "")
            content = b.get(btype, {})
            rich = content.get("rich_text", [])
            text = "".join(t.get("plain_text", "") for t in rich)
            info(f"  [{btype}] {text[:60]}")
    else:
        fail(f"블록 읽기 실패 — {r.status_code}: {r.text}")
else:
    info("접근 가능한 페이지가 없어 블록 읽기를 건너뜁니다.")


# ── 5. 페이지 생성 ────────────────────────────────────────
section("5. 페이지 생성 — 테스트 페이지 (첫 번째 페이지 하위)")
created_page_id = None
if accessible_pages:
    parent_id = accessible_pages[0]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": f"[API 테스트] {now_str}"}}]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Notion API 연동 테스트로 생성된 페이지입니다."},
                        }
                    ]
                },
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "생성 시각: " + now_str}}]
                },
            },
        ],
    }
    r = requests.post(f"{BASE_URL}/pages", headers=HEADERS, json=payload)
    if r.status_code == 200:
        data = r.json()
        created_page_id = data.get("id")
        ok(f"페이지 생성 성공 — id={created_page_id}")
        url = data.get("url", "")
        info(f"  URL: {url}")
    else:
        fail(f"페이지 생성 실패 — {r.status_code}: {r.text[:200]}")
else:
    info("부모 페이지가 없어 생성 테스트를 건너뜁니다.")


# ── 6. 페이지 업데이트 ────────────────────────────────────
section("6. 페이지 업데이트 — 생성한 테스트 페이지에 아이콘 추가")
if created_page_id:
    payload = {"icon": {"type": "emoji", "emoji": "✅"}}
    r = requests.patch(f"{BASE_URL}/pages/{created_page_id}", headers=HEADERS, json=payload)
    if r.status_code == 200:
        ok(f"페이지 업데이트 성공 (아이콘 ✅ 설정)")
    else:
        fail(f"업데이트 실패 — {r.status_code}: {r.text[:200]}")
else:
    info("생성된 페이지가 없어 업데이트를 건너뜁니다.")


# ── 요약 ──────────────────────────────────────────────────
section("테스트 완료 요약")
info(f"접근 가능한 페이지 수 : {len(accessible_pages)}")
info(f"접근 가능한 DB 수     : {len(accessible_dbs)}")
info(f"생성된 테스트 페이지  : {created_page_id or '없음'}")
print()
