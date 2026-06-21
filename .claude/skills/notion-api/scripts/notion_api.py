"""
Notion API 전용 헬퍼 스크립트
MCP로 불가능한 작업들을 처리한다.

사용법:
  python -X utf8 notion_api.py <command> [args]

Commands:
  list-blocks   <page_id>                         페이지 블록 목록 조회
  update-block  <block_id> <text>                 블록 텍스트 수정
  delete-block  <block_id>                        블록 삭제
  archive-page  <page_id>                         페이지 아카이브(삭제)
  restore-page  <page_id>                         페이지 복원
  bulk-archive  <page_id1,page_id2,...>           여러 페이지 일괄 아카이브
  detect-changes <db_id> [hours_ago]              DB 변경 감지 (기본 24시간)
  update-schema  <db_id> <json_file>              DB 스키마 수정
  list-db-props  <db_id>                          DB 속성 목록 조회
  bulk-assign    <db_id> <user_id> <filter_json>  조건에 맞는 항목 담당자 일괄 지정
"""

import os
import sys
import io
import json
import time
import argparse
import requests
from datetime import datetime, timezone, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}

RATE_LIMIT_SLEEP = 0.4  # 초당 3요청 제한 대응


def ok(msg):   print(f"[OK] {msg}")
def fail(msg): print(f"[FAIL] {msg}"); sys.exit(1)
def info(msg): print(f"  {msg}")


def get(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
    if r.status_code not in (200, 201):
        fail(f"GET {path} -> {r.status_code}: {r.text[:300]}")
    return r.json()


def patch(path, body):
    r = requests.patch(f"{BASE_URL}{path}", headers=HEADERS, json=body)
    if r.status_code not in (200, 201):
        fail(f"PATCH {path} -> {r.status_code}: {r.text[:300]}")
    return r.json()


def delete(path):
    r = requests.delete(f"{BASE_URL}{path}", headers=HEADERS)
    if r.status_code not in (200, 201):
        fail(f"DELETE {path} -> {r.status_code}: {r.text[:300]}")
    return r.json()


def post(path, body):
    r = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=body)
    if r.status_code not in (200, 201):
        fail(f"POST {path} -> {r.status_code}: {r.text[:300]}")
    return r.json()


# ── 1. 블록 목록 조회 ─────────────────────────────────────
def cmd_list_blocks(page_id):
    data = get(f"/blocks/{page_id}/children", {"page_size": 50})
    blocks = data.get("results", [])
    ok(f"블록 {len(blocks)}개 조회 (page_id={page_id})")
    for i, b in enumerate(blocks):
        btype = b.get("type", "")
        bid = b.get("id", "")
        content = b.get(btype, {})
        rich = content.get("rich_text", [])
        text = "".join(t.get("plain_text", "") for t in rich)[:60]
        info(f"[{i}] id={bid} type={btype} | {text or '(내용 없음)'}")
    return blocks


# ── 2. 블록 수정 ──────────────────────────────────────────
def cmd_update_block(block_id, new_text):
    # 현재 블록 타입 확인
    b = get(f"/blocks/{block_id}")
    btype = b.get("type", "paragraph")
    body = {
        btype: {
            "rich_text": [{"type": "text", "text": {"content": new_text}}]
        }
    }
    patch(f"/blocks/{block_id}", body)
    ok(f"블록 수정 완료 (id={block_id})")
    info(f"내용: {new_text[:80]}")


# ── 3. 블록 삭제 ──────────────────────────────────────────
def cmd_delete_block(block_id):
    delete(f"/blocks/{block_id}")
    ok(f"블록 삭제 완료 (id={block_id})")


# ── 4. 페이지 아카이브 ────────────────────────────────────
def cmd_archive_page(page_id):
    patch(f"/pages/{page_id}", {"archived": True})
    ok(f"페이지 아카이브 완료 (id={page_id})")
    info("복원: python notion_api.py restore-page <page_id>")


# ── 5. 페이지 복원 ────────────────────────────────────────
def cmd_restore_page(page_id):
    patch(f"/pages/{page_id}", {"archived": False})
    ok(f"페이지 복원 완료 (id={page_id})")


# ── 6. 여러 페이지 일괄 아카이브 ─────────────────────────
def cmd_bulk_archive(page_ids_str):
    ids = [p.strip() for p in page_ids_str.split(",") if p.strip()]
    ok(f"총 {len(ids)}개 페이지 아카이브 시작")
    success, failed = 0, []
    for pid in ids:
        try:
            patch(f"/pages/{pid}", {"archived": True})
            info(f"  아카이브: {pid}")
            success += 1
        except SystemExit:
            failed.append(pid)
        time.sleep(RATE_LIMIT_SLEEP)
    print(f"\n완료: 성공 {success}개 / 실패 {len(failed)}개")
    if failed:
        info(f"실패 목록: {failed}")


# ── 7. DB 변경 감지 ───────────────────────────────────────
def cmd_detect_changes(db_id, hours_ago=24):
    since = (datetime.now(timezone.utc) - timedelta(hours=int(hours_ago))).isoformat()
    body = {
        "filter": {
            "timestamp": "last_edited_time",
            "last_edited_time": {"after": since}
        },
        "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
        "page_size": 50
    }
    data = post(f"/databases/{db_id}/query", body)
    results = data.get("results", [])
    ok(f"최근 {hours_ago}시간 내 변경된 항목: {len(results)}개")
    for item in results:
        pid = item.get("id", "")
        edited = item.get("last_edited_time", "")
        editor = item.get("last_edited_by", {}).get("id", "unknown")
        props = item.get("properties", {})
        title = ""
        for v in props.values():
            if v.get("type") == "title":
                title = "".join(t.get("plain_text", "") for t in v.get("title", []))
                break
        info(f"  [{edited[:16]}] {title[:40] or '(제목 없음)'} | by={editor[:8]}... | id={pid[:8]}...")
    return results


# ── 8. DB 스키마 조작 ─────────────────────────────────────
def cmd_update_schema(db_id, json_file):
    with open(json_file, encoding="utf-8") as f:
        props = json.load(f)
    body = {"properties": props}
    patch(f"/databases/{db_id}", body)
    ok(f"DB 스키마 업데이트 완료 (db_id={db_id})")
    info(f"변경 속성: {list(props.keys())}")


# ── 9. DB 속성 목록 조회 ─────────────────────────────────
def cmd_list_db_props(db_id):
    data = get(f"/databases/{db_id}")
    props = data.get("properties", {})
    title_arr = data.get("title", [])
    db_title = "".join(t.get("plain_text", "") for t in title_arr)
    ok(f"DB '{db_title}' 속성 {len(props)}개")
    for name, prop in props.items():
        ptype = prop.get("type", "")
        info(f"  {name:<30} [{ptype}]")


# ── 10. 담당자 일괄 지정 ─────────────────────────────────
def cmd_bulk_assign(db_id, user_id, filter_json_str):
    try:
        filter_body = json.loads(filter_json_str)
    except json.JSONDecodeError:
        fail("filter_json 파싱 실패. 올바른 JSON 문자열을 입력하세요.")

    # 대상 페이지 조회
    data = post(f"/databases/{db_id}/query", {"filter": filter_body, "page_size": 100})
    pages = data.get("results", [])
    ok(f"대상 페이지 {len(pages)}개 조회")

    if not pages:
        info("업데이트할 항목이 없습니다.")
        return

    # People 속성 이름 찾기
    db_data = get(f"/databases/{db_id}")
    people_prop = None
    for name, prop in db_data.get("properties", {}).items():
        if prop.get("type") == "people":
            people_prop = name
            break

    if not people_prop:
        fail("DB에 People(담당자) 속성이 없습니다.")

    success = 0
    for page in pages:
        pid = page.get("id")
        try:
            patch(f"/pages/{pid}", {
                "properties": {
                    people_prop: {
                        "people": [{"object": "user", "id": user_id}]
                    }
                }
            })
            success += 1
        except SystemExit:
            pass
        time.sleep(RATE_LIMIT_SLEEP)

    ok(f"담당자 일괄 지정 완료: {success}/{len(pages)}개 (속성: '{people_prop}')")


# ── CLI 진입점 ────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "list-blocks":
        if len(sys.argv) < 3: fail("page_id 필요")
        cmd_list_blocks(sys.argv[2])

    elif cmd == "update-block":
        if len(sys.argv) < 4: fail("block_id, text 필요")
        cmd_update_block(sys.argv[2], sys.argv[3])

    elif cmd == "delete-block":
        if len(sys.argv) < 3: fail("block_id 필요")
        cmd_delete_block(sys.argv[2])

    elif cmd == "archive-page":
        if len(sys.argv) < 3: fail("page_id 필요")
        cmd_archive_page(sys.argv[2])

    elif cmd == "restore-page":
        if len(sys.argv) < 3: fail("page_id 필요")
        cmd_restore_page(sys.argv[2])

    elif cmd == "bulk-archive":
        if len(sys.argv) < 3: fail("page_ids(콤마 구분) 필요")
        cmd_bulk_archive(sys.argv[2])

    elif cmd == "detect-changes":
        if len(sys.argv) < 3: fail("db_id 필요")
        hours = sys.argv[3] if len(sys.argv) > 3 else "24"
        cmd_detect_changes(sys.argv[2], hours)

    elif cmd == "update-schema":
        if len(sys.argv) < 4: fail("db_id, json_file 필요")
        cmd_update_schema(sys.argv[2], sys.argv[3])

    elif cmd == "list-db-props":
        if len(sys.argv) < 3: fail("db_id 필요")
        cmd_list_db_props(sys.argv[2])

    elif cmd == "bulk-assign":
        if len(sys.argv) < 5: fail("db_id, user_id, filter_json 필요")
        cmd_bulk_assign(sys.argv[2], sys.argv[3], sys.argv[4])

    else:
        fail(f"알 수 없는 명령: {cmd}\n\n사용법:\n{__doc__}")


if __name__ == "__main__":
    main()
