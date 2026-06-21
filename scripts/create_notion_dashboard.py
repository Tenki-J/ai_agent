"""
테스트용 Notion 대시보드 생성 스크립트
API로만 가능한 풍부한 블록 구성을 사용
"""
import os
import sys, io, requests, json
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

# 부모 페이지 (Notion API 테스트 페이지)
PARENT_PAGE_ID = "38663685-d218-80a5-b9c2-e418b2cb9c60"

today = datetime.now().strftime("%Y년 %m월 %d일")
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")


def rt(text, bold=False, color="default"):
    """rich_text 객체 생성 헬퍼"""
    obj = {"type": "text", "text": {"content": text}}
    if bold or color != "default":
        obj["annotations"] = {}
        if bold:
            obj["annotations"]["bold"] = True
        if color != "default":
            obj["annotations"]["color"] = color
    return obj


def heading1(text):
    return {"object": "block", "type": "heading_1",
            "heading_1": {"rich_text": [rt(text)]}}

def heading2(text):
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": [rt(text)]}}

def heading3(text):
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [rt(text)]}}

def paragraph(text, bold=False, color="default"):
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [rt(text, bold, color)]}}

def callout(text, emoji="📌"):
    return {"object": "block", "type": "callout",
            "callout": {"rich_text": [rt(text)], "icon": {"type": "emoji", "emoji": emoji}}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def bullet(text, bold=False):
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [rt(text, bold)]}}

def numbered(text):
    return {"object": "block", "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": [rt(text)]}}

def toggle(text, children=None):
    block = {"object": "block", "type": "toggle",
             "toggle": {"rich_text": [rt(text, bold=True)]}}
    if children:
        block["toggle"]["children"] = children
    return block

def quote(text):
    return {"object": "block", "type": "quote",
            "quote": {"rich_text": [rt(text)]}}

def todo(text, checked=False):
    return {"object": "block", "type": "to_do",
            "to_do": {"rich_text": [rt(text)], "checked": checked}}


# ── 대시보드 블록 구성 ─────────────────────────────────────
blocks = [
    # 헤더 섹션
    callout(f"마지막 업데이트: {now_str}  |  Notion API 자동 생성", "🤖"),
    divider(),

    # 개요 섹션
    heading2("📊 개요"),
    paragraph("이 대시보드는 Notion API 직접 호출로 생성되었습니다. MCP 툴로는 불가능한 블록 구조를 포함합니다."),
    divider(),

    # API 기능 현황 섹션
    heading2("⚙️ API 전용 기능 현황"),
    bullet("블록 직접 수정 / 삭제", bold=True),
    bullet("  → block_id 타겟팅 후 PATCH/DELETE 호출"),
    bullet("페이지 아카이브(삭제)", bold=True),
    bullet("  → archived: true 설정"),
    bullet("대량 배치 처리", bold=True),
    bullet("  → 루프 + Rate limit(0.4s) 자동 관리"),
    bullet("변경 감지 polling", bold=True),
    bullet("  → last_edited_time 필터 쿼리"),
    bullet("DB 스키마 세밀 조작", bold=True),
    bullet("  → 속성 추가·삭제·이름 변경"),
    divider(),

    # 작업 체크리스트 섹션
    heading2("✅ 테스트 체크리스트"),
    todo("연결 확인 (GET /users/me)", checked=True),
    todo("페이지 읽기 (GET /pages/{id})", checked=True),
    todo("블록 읽기 (GET /blocks/{id}/children)", checked=True),
    todo("블록 수정 (PATCH /blocks/{id})", checked=True),
    todo("페이지 생성 (POST /pages)", checked=True),
    todo("페이지 아카이브 / 복원", checked=True),
    todo("대시보드 페이지 생성", checked=False),
    todo("하위 데이터베이스 생성", checked=False),
    divider(),

    # 토글 — 사용 방법
    heading2("📖 스킬 사용 방법"),
    toggle("블록 수정 예시", children=[
        paragraph("python -X utf8 .claude/skills/notion-api/scripts/notion_api.py update-block <block_id> '새 내용'"),
    ]),
    toggle("페이지 아카이브 예시", children=[
        paragraph("python -X utf8 .claude/skills/notion-api/scripts/notion_api.py archive-page <page_id>"),
    ]),
    toggle("변경 감지 예시 (최근 24시간)", children=[
        paragraph("python -X utf8 .claude/skills/notion-api/scripts/notion_api.py detect-changes <db_id> 24"),
    ]),
    divider(),

    # 비교표 섹션
    heading2("🔍 MCP vs API 요약"),
    quote("MCP: 일회성·대화형 작업 / API: 자동화·배치·시스템 연동"),
    paragraph("MCP로 충분한 경우", bold=True),
    numbered("페이지 생성·수정·검색"),
    numbered("DB 쿼리 및 SQL 필터"),
    numbered("댓글 작성·조회"),
    paragraph("API가 필요한 경우", bold=True),
    numbered("블록 ID 직접 수정·삭제"),
    numbered("페이지 아카이브"),
    numbered("대량 일괄 처리 (수백~수천 건)"),
    numbered("이벤트 기반 자동화 (Webhook, 크론)"),
    divider(),

    # 푸터
    paragraph(f"생성일: {today}  |  Integration: JH_API  |  skill: notion-api", color="gray"),
]

# ── API 호출: 대시보드 페이지 생성 ────────────────────────
print(f"대시보드 생성 중...")
payload = {
    "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
    "icon": {"type": "emoji", "emoji": "📊"},
    "cover": {
        "type": "external",
        "external": {"url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200"}
    },
    "properties": {
        "title": {
            "title": [{"type": "text", "text": {"content": f"📊 API 테스트 대시보드 — {today}"}}]
        }
    },
    "children": blocks
}

r = requests.post(f"{BASE_URL}/pages", headers=HEADERS, json=payload)

if r.status_code == 200:
    data = r.json()
    page_id = data.get("id")
    url = data.get("url", "")
    print(f"\n[OK] 대시보드 생성 성공!")
    print(f"  페이지 ID : {page_id}")
    print(f"  URL       : {url}")
    print(f"  블록 수   : {len(blocks)}개")
else:
    print(f"[FAIL] {r.status_code}: {r.text[:500]}")
