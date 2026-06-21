"""
'Notion API 테스트 페이지'를 '일정 관리 페이지'로 재구성
1. 페이지 제목 변경
2. 기존 테스트 블록 삭제
3. 이전 테스트 child_page 아카이브
4. 인트로 섹션 블록 추가
5. 일정 관리 DB 생성 (Properties 풀구성)
"""
import os
import sys, io, requests, time
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION, "Content-Type": "application/json"}

PAGE_ID = "38663685-d218-80a5-b9c2-e418b2cb9c60"

# 정리 대상 블록 (테스트 paragraph + 이전 테스트 child_page 2개)
BLOCKS_TO_DELETE  = ["38663685-d218-8087-9cc4-cfeabfad083d"]   # paragraph (테스트 수정 내용)
PAGES_TO_ARCHIVE  = [
    "38663685-d218-8172-9078-cc3951cc68d1",   # [API 테스트] 생성 페이지
    "38663685-d218-81dc-b0f1-fda8a7f4d12c",   # 📊 API 테스트 대시보드
]

today = datetime.now().strftime("%Y년 %m월 %d일")


def ok(msg):  print(f"[OK] {msg}")
def step(msg): print(f"\n── {msg}")
def info(msg): print(f"    {msg}")


def patch(path, body):
    r = requests.patch(f"{BASE}{path}", headers=H, json=body)
    if r.status_code not in (200, 201):
        print(f"[FAIL] PATCH {path} → {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    return r.json()

def delete(path):
    r = requests.delete(f"{BASE}{path}", headers=H)
    if r.status_code not in (200, 201):
        print(f"[FAIL] DELETE {path} → {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    return r.json()

def post(path, body):
    r = requests.post(f"{BASE}{path}", headers=H, json=body)
    if r.status_code not in (200, 201):
        print(f"[FAIL] POST {path} → {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    return r.json()


# ── STEP 1. 페이지 제목 변경 ──────────────────────────────
step("STEP 1. 페이지 제목 변경")
patch(f"/pages/{PAGE_ID}", {
    "icon": {"type": "emoji", "emoji": "📅"},
    "properties": {
        "title": {
            "title": [{"type": "text", "text": {"content": "📅 일정 관리 페이지"}}]
        }
    }
})
ok("제목 → '📅 일정 관리 페이지'")


# ── STEP 2. 기존 테스트 블록 삭제 ────────────────────────
step("STEP 2. 기존 테스트 블록 삭제")
for bid in BLOCKS_TO_DELETE:
    delete(f"/blocks/{bid}")
    ok(f"블록 삭제: {bid[:8]}...")
    time.sleep(0.4)


# ── STEP 3. 이전 테스트 페이지 아카이브 ──────────────────
step("STEP 3. 이전 테스트 child_page 아카이브")
for pid in PAGES_TO_ARCHIVE:
    patch(f"/pages/{pid}", {"archived": True})
    ok(f"아카이브: {pid[:8]}...")
    time.sleep(0.4)


# ── STEP 4. 인트로 섹션 블록 추가 ────────────────────────
step("STEP 4. 인트로 섹션 추가")

def rt(text, bold=False, color="default"):
    obj = {"type": "text", "text": {"content": text}}
    ann = {}
    if bold: ann["bold"] = True
    if color != "default": ann["color"] = color
    if ann: obj["annotations"] = ann
    return obj

intro_blocks = [
    {
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": [rt("이 페이지는 일정 관리 전용 공간입니다. 하단 데이터베이스에서 일정을 추가·수정하세요.")],
            "icon": {"type": "emoji", "emoji": "📌"},
            "color": "blue_background"
        }
    },
    {"object": "block", "type": "divider", "divider": {}},
    {
        "object": "block", "type": "heading_2",
        "heading_2": {"rich_text": [rt("📋 이 페이지 사용 방법")]}
    },
    {
        "object": "block", "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": [rt("아래 일정 DB에서 ", False), rt("+ New", True), rt(" 를 눌러 일정을 추가합니다.")]}
    },
    {
        "object": "block", "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": [rt("날짜 / 상태 / 우선순위 / 카테고리를 설정합니다.")]}
    },
    {
        "object": "block", "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": [rt("상태를 '진행 중' → '완료'로 업데이트하며 진행 상황을 추적합니다.")]}
    },
    {"object": "block", "type": "divider", "divider": {}},
    {
        "object": "block", "type": "heading_2",
        "heading_2": {"rich_text": [rt("🗂️ 일정 데이터베이스")]}
    },
]

patch(f"/blocks/{PAGE_ID}/children", {"children": intro_blocks})
ok(f"인트로 블록 {len(intro_blocks)}개 추가")


# ── STEP 5. 일정 관리 DB 생성 ─────────────────────────────
step("STEP 5. 일정 관리 데이터베이스 생성")

db_payload = {
    "parent": {"type": "page_id", "page_id": PAGE_ID},
    "icon": {"type": "emoji", "emoji": "🗓️"},
    "title": [{"type": "text", "text": {"content": "일정 관리"}}],
    "is_inline": True,   # 페이지 내 인라인 DB
    "properties": {
        # ① 제목 (필수)
        "일정 제목": {"title": {}},

        # ② 날짜 (시작일·종료일)
        "날짜": {"date": {}},

        # ③ 상태
        "상태": {
            "select": {
                "options": [
                    {"name": "예정",    "color": "gray"},
                    {"name": "진행 중", "color": "blue"},
                    {"name": "완료",    "color": "green"},
                    {"name": "취소",    "color": "red"},
                    {"name": "보류",    "color": "yellow"},
                ]
            }
        },

        # ④ 우선순위
        "우선순위": {
            "select": {
                "options": [
                    {"name": "🔴 높음", "color": "red"},
                    {"name": "🟡 보통", "color": "yellow"},
                    {"name": "🟢 낮음", "color": "green"},
                ]
            }
        },

        # ⑤ 카테고리 (복수 선택)
        "카테고리": {
            "multi_select": {
                "options": [
                    {"name": "업무",   "color": "blue"},
                    {"name": "회의",   "color": "purple"},
                    {"name": "개인",   "color": "pink"},
                    {"name": "교육",   "color": "orange"},
                    {"name": "기타",   "color": "gray"},
                ]
            }
        },

        # ⑥ 담당자
        "담당자": {"people": {}},

        # ⑦ 메모
        "메모": {"rich_text": {}},

        # ⑧ 자동 생성 시간
        "생성일": {"created_time": {}},

        # ⑨ 마지막 수정 시간
        "수정일": {"last_edited_time": {}},
    }
}

db = post("/databases", db_payload)
db_id  = db.get("id", "")
db_url = db.get("url", "")
ok(f"DB 생성 완료")
info(f"DB ID  : {db_id}")
info(f"DB URL : {db_url}")


# ── STEP 6. 샘플 일정 3건 추가 ────────────────────────────
step("STEP 6. 샘플 일정 데이터 추가")

samples = [
    {
        "일정 제목": "팀 주간 회의",
        "날짜": "2026-06-23",
        "상태": "예정",
        "우선순위": "🔴 높음",
        "카테고리": ["회의", "업무"],
        "메모": "주간 업무 공유 및 이슈 논의"
    },
    {
        "일정 제목": "Notion API 스킬 개발 완료 검토",
        "날짜": "2026-06-21",
        "상태": "진행 중",
        "우선순위": "🟡 보통",
        "카테고리": ["업무", "교육"],
        "메모": "notion-api 스킬 테스트 및 문서화"
    },
    {
        "일정 제목": "월간 일정 리뷰",
        "날짜": "2026-06-30",
        "상태": "예정",
        "우선순위": "🟢 낮음",
        "카테고리": ["개인"],
        "메모": "6월 마무리 및 7월 계획 수립"
    },
]

for s in samples:
    props = {
        "일정 제목": {"title": [{"type": "text", "text": {"content": s["일정 제목"]}}]},
        "날짜": {"date": {"start": s["날짜"]}},
        "상태": {"select": {"name": s["상태"]}},
        "우선순위": {"select": {"name": s["우선순위"]}},
        "카테고리": {"multi_select": [{"name": c} for c in s["카테고리"]]},
        "메모": {"rich_text": [{"type": "text", "text": {"content": s["메모"]}}]},
    }
    post("/pages", {"parent": {"database_id": db_id}, "properties": props})
    ok(f"샘플 추가: {s['일정 제목']}")
    time.sleep(0.4)


# ── 완료 요약 ─────────────────────────────────────────────
print(f"""
{'='*55}
  재구성 완료
{'='*55}
  페이지 제목  : 📅 일정 관리 페이지
  정리된 블록  : {len(BLOCKS_TO_DELETE)}개 삭제, {len(PAGES_TO_ARCHIVE)}개 아카이브
  인트로 블록  : {len(intro_blocks)}개 추가
  일정 관리 DB : 9개 속성, 샘플 {len(samples)}건
  DB ID        : {db_id}
  페이지 URL   : https://notion.so/{PAGE_ID.replace('-', '')}
""")
