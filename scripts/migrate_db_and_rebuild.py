"""
일정 관리 DB 이동 및 캘린더 페이지 재구성
STEP 1. 새 DB 전용 페이지 생성
STEP 2. 동일 스키마로 새 DB 생성
STEP 3. 15개 항목 데이터 마이그레이션
STEP 4. 캘린더 페이지 기존 블록 전체 삭제 (구 DB 포함 아카이브)
STEP 5. 캘린더 페이지 재구성 (링크 + 캘린더 뷰 추가 안내)
"""
import os
import sys, io, requests, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN   = os.environ.get("NOTION_TOKEN")
VERSION = "2022-06-28"
BASE    = "https://api.notion.com/v1"
H       = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION,
           "Content-Type": "application/json"}

OLD_DB_ID       = "38663685-d218-81aa-9ec4-eecd8a8e538a"
CALENDAR_PG_ID  = "38663685-d218-80a5-b9c2-e418b2cb9c60"

# 캘린더 페이지 기존 블록 ID 목록 (child_database 포함)
OLD_BLOCK_IDS = [
    "38663685-d218-81a0-a42b-daed90830920",  # callout
    "38663685-d218-813f-9f0d-eb345bc84189",  # divider
    "38663685-d218-81e7-b410-f79e1d547c6e",  # heading_2
    "38663685-d218-81e6-8b01-f4697d0208f5",  # numbered_list_item
    "38663685-d218-81b9-9519-c9ccc67b1d70",  # numbered_list_item
    "38663685-d218-81eb-bcb7-da49e6ccbb99",  # numbered_list_item
    "38663685-d218-8116-8e03-c181cc841580",  # divider
    "38663685-d218-817d-93e6-e586a45aba63",  # heading_2
    "38663685-d218-81aa-9ec4-eecd8a8e538a",  # child_database (구 DB)
]

def ok(msg):    print(f"  [OK] {msg}")
def info(msg):  print(f"       {msg}")
def step(title): print(f"\n{'─'*55}\n  {title}\n{'─'*55}")

def get(path):
    r = requests.get(f"{BASE}{path}", headers=H)
    if r.status_code not in (200, 201): raise RuntimeError(f"GET {path} → {r.status_code}: {r.text[:200]}")
    return r.json()

def post(path, body):
    r = requests.post(f"{BASE}{path}", headers=H, json=body)
    if r.status_code not in (200, 201): raise RuntimeError(f"POST {path} → {r.status_code}: {r.text[:300]}")
    return r.json()

def patch(path, body):
    r = requests.patch(f"{BASE}{path}", headers=H, json=body)
    if r.status_code not in (200, 201): raise RuntimeError(f"PATCH {path} → {r.status_code}: {r.text[:300]}")
    return r.json()

def delete(path):
    r = requests.delete(f"{BASE}{path}", headers=H)
    if r.status_code not in (200, 201): raise RuntimeError(f"DELETE {path} → {r.status_code}: {r.text[:200]}")
    return r.json()


# ══════════════════════════════════════════════════════════
# STEP 1. 새 DB 전용 페이지 생성
# ══════════════════════════════════════════════════════════
step("STEP 1. 새 DB 전용 페이지 생성")

new_db_page = post("/pages", {
    "parent": {"type": "page_id", "page_id": CALENDAR_PG_ID},
    "icon":   {"type": "emoji", "emoji": "🗓️"},
    "properties": {
        "title": {"title": [{"type": "text", "text": {"content": "🗓️ 일정 관리 DB"}}]}
    }
})
NEW_DB_PAGE_ID = new_db_page["id"]
NEW_DB_PAGE_URL = new_db_page["url"]
ok(f"새 페이지 생성 완료")
info(f"ID  : {NEW_DB_PAGE_ID}")
info(f"URL : {NEW_DB_PAGE_URL}")


# ══════════════════════════════════════════════════════════
# STEP 2. 동일 스키마로 새 DB 생성
# ══════════════════════════════════════════════════════════
step("STEP 2. 새 페이지에 DB 생성 (동일 스키마)")

new_db = post("/databases", {
    "parent": {"type": "page_id", "page_id": NEW_DB_PAGE_ID},
    "icon":   {"type": "emoji", "emoji": "📋"},
    "title":  [{"type": "text", "text": {"content": "일정 관리"}}],
    "is_inline": False,
    "properties": {
        "일정 제목": {"title": {}},
        "날짜":     {"date": {}},
        "상태": {
            "select": {"options": [
                {"name": "예정",    "color": "gray"},
                {"name": "진행 중", "color": "blue"},
                {"name": "완료",    "color": "green"},
                {"name": "취소",    "color": "red"},
                {"name": "보류",    "color": "yellow"},
            ]}
        },
        "우선순위": {
            "select": {"options": [
                {"name": "🔴 높음", "color": "red"},
                {"name": "🟡 보통", "color": "yellow"},
                {"name": "🟢 낮음", "color": "green"},
            ]}
        },
        "카테고리": {
            "multi_select": {"options": [
                {"name": "업무",   "color": "blue"},
                {"name": "회의",   "color": "purple"},
                {"name": "개인",   "color": "pink"},
                {"name": "교육",   "color": "orange"},
                {"name": "기타",   "color": "gray"},
            ]}
        },
        "담당자": {"people": {}},
        "메모":   {"rich_text": {}},
        "생성일": {"created_time": {}},
        "수정일": {"last_edited_time": {}},
    }
})
NEW_DB_ID = new_db["id"]
ok(f"새 DB 생성 완료")
info(f"DB ID : {NEW_DB_ID}")


# ══════════════════════════════════════════════════════════
# STEP 3. 기존 15개 항목 마이그레이션
# ══════════════════════════════════════════════════════════
step("STEP 3. 데이터 마이그레이션 (15개 항목)")

entries = post(f"/databases/{OLD_DB_ID}/query", {"page_size": 100})["results"]
ok(f"기존 항목 조회: {len(entries)}개")

migrated = 0
for e in entries:
    p = e["properties"]

    # 제목
    title_text = "".join(t["plain_text"] for t in p["일정 제목"]["title"])

    # 날짜
    date_val = p["날짜"]["date"]

    # 상태
    status_sel = p["상태"]["select"]
    status_val = {"select": {"name": status_sel["name"]}} if status_sel else {"select": None}

    # 우선순위
    prio_sel = p["우선순위"]["select"]
    prio_val = {"select": {"name": prio_sel["name"]}} if prio_sel else {"select": None}

    # 카테고리
    cats = [{"name": c["name"]} for c in p["카테고리"]["multi_select"]]

    # 메모
    memo_text = "".join(t["plain_text"] for t in p["메모"]["rich_text"])

    new_props = {
        "일정 제목": {"title": [{"type": "text", "text": {"content": title_text}}]},
        "날짜":      {"date": date_val},
        "상태":      status_val,
        "우선순위":  prio_val,
        "카테고리":  {"multi_select": cats},
        "메모":      {"rich_text": [{"type": "text", "text": {"content": memo_text}}] if memo_text else []},
    }

    post("/pages", {"parent": {"database_id": NEW_DB_ID}, "properties": new_props})
    migrated += 1
    info(f"[{migrated:02d}/15] {title_text[:45]}")
    time.sleep(0.4)

ok(f"마이그레이션 완료: {migrated}개")


# ══════════════════════════════════════════════════════════
# STEP 4. 캘린더 페이지 기존 블록 전체 삭제 (구 DB 아카이브 포함)
# ══════════════════════════════════════════════════════════
step("STEP 4. 캘린더 페이지 기존 블록 정리")

for bid in OLD_BLOCK_IDS:
    delete(f"/blocks/{bid}")
    info(f"삭제: {bid[:8]}...")
    time.sleep(0.35)

ok(f"{len(OLD_BLOCK_IDS)}개 블록 삭제 완료 (구 DB 아카이브)")


# ══════════════════════════════════════════════════════════
# STEP 5. 캘린더 페이지 재구성
# ══════════════════════════════════════════════════════════
step("STEP 5. 캘린더 페이지 재구성")

def rt(text, bold=False, color="default"):
    obj = {"type": "text", "text": {"content": text}}
    ann = {}
    if bold:            ann["bold"] = True
    if color != "default": ann["color"] = color
    if ann:             obj["annotations"] = ann
    return obj

def page_mention(page_id):
    return {
        "type": "mention",
        "mention": {"type": "page", "page": {"id": page_id}},
        "plain_text": "🗓️ 일정 관리 DB",
    }

new_blocks = [
    # ── 상단 안내 ─────────────────────────────────────────
    {
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": [
                rt("일정 데이터는 하위 페이지 "),
                page_mention(NEW_DB_PAGE_ID),
                rt(" 에서 관리됩니다. 아래 캘린더 뷰를 추가하면 이 페이지에서 바로 확인할 수 있습니다.")
            ],
            "icon": {"type": "emoji", "emoji": "📌"},
            "color": "blue_background"
        }
    },
    {"object": "block", "type": "divider", "divider": {}},

    # ── 캘린더 뷰 추가 안내 ───────────────────────────────
    {
        "object": "block", "type": "heading_2",
        "heading_2": {"rich_text": [rt("📅 캘린더 뷰 추가 방법 (Notion UI)")]}
    },
    {
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": [
                rt("Notion API는 '연결된 DB 뷰(Linked Database View)' 삽입을 지원하지 않습니다.\n"
                   "아래 2단계를 따라 직접 추가하면 이 페이지에 캘린더가 표시됩니다.", color="gray")
            ],
            "icon": {"type": "emoji", "emoji": "ℹ️"},
            "color": "gray_background"
        }
    },
    {
        "object": "block", "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [rt("이 페이지에서 "), rt("/linked", bold=True), rt(" 입력 → "), rt("'Create linked database'", bold=True), rt(" 선택")]
        }
    },
    {
        "object": "block", "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [rt("검색창에 "), rt("'일정 관리'", bold=True), rt(" 입력 → DB 선택 → 상단 뷰 탭에서 "), rt("'+ Add view' → Calendar", bold=True), rt(" 선택")]
        }
    },
    {"object": "block", "type": "divider", "divider": {}},

    # ── DB 바로가기 ───────────────────────────────────────
    {
        "object": "block", "type": "heading_2",
        "heading_2": {"rich_text": [rt("🔗 일정 관리 DB 바로가기")]}
    },
    {
        "object": "block", "type": "paragraph",
        "paragraph": {
            "rich_text": [
                rt("→  "),
                page_mention(NEW_DB_PAGE_ID),
            ]
        }
    },
    {"object": "block", "type": "divider", "divider": {}},

    # ── 일정 요약 ─────────────────────────────────────────
    {
        "object": "block", "type": "heading_2",
        "heading_2": {"rich_text": [rt("🗒️ 주요 일정 요약")]}
    },
    {
        "object": "block", "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [rt("🎮 지스타 2026 BTC 전시", bold=True), rt("  |  2026-11-19 ~ 11-22  |  부산 벡스코")]}
    },
    {
        "object": "block", "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [rt("🎟️ 입장권 예매 오픈 (예상)", bold=True), rt("  |  2026-10-15  |  예스24 단독")]}
    },
    {
        "object": "block", "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [rt("⏰ 취소·환불 마감", bold=True), rt("  |  관람 전일 17:00까지")]}
    },
]

patch(f"/blocks/{CALENDAR_PG_ID}/children", {"children": new_blocks})
ok(f"캘린더 페이지 재구성 완료 ({len(new_blocks)}개 블록)")


# ── 최종 요약 ─────────────────────────────────────────────
print(f"""
{'═'*55}
  완료 요약
{'═'*55}
  [생성] 새 DB 전용 페이지 : 🗓️ 일정 관리 DB
         URL: {NEW_DB_PAGE_URL}

  [생성] 새 DB (동일 스키마): {NEW_DB_ID}

  [이동] 데이터 마이그레이션: {migrated}개 항목

  [정리] 캘린더 페이지 재구성 완료
         구 DB 아카이브 + {len(new_blocks)}개 신규 블록

  [안내] 캘린더 뷰 연동
         Notion UI에서 /linked 입력 → 일정 관리 DB 선택
         → Calendar 뷰 선택 (2단계)
""")
