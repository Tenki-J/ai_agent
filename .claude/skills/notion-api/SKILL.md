---
name: notion-api
description: >
  Notion API 직접 호출이 필요한 작업을 처리하는 스킬.
  Notion MCP 툴(notion-create-pages, notion-update-page 등)로 할 수 없는 작업에 반드시 이 스킬을 사용한다.
  다음 표현이 나오면 항상 이 스킬을 사용한다:
  "블록 삭제", "블록 수정", "페이지 삭제", "페이지 아카이브", "휴지통", "일괄 처리", "대량 업데이트",
  "변경 감지", "DB 스키마 수정", "속성 추가/삭제", "notion api", "api로 처리해줘".
  Notion MCP가 활성화되어 있어도 위 작업은 이 스킬을 통해 처리한다.
allowed-tools: [Bash, PowerShell, Read, Write, Edit]
---

# Notion API 스킬

## MCP vs API — 이 스킬이 담당하는 영역

Notion MCP 툴이 지원하지 않아 API 직접 호출이 필요한 작업들:

| 작업 | 이유 |
|------|------|
| 블록 수정 / 삭제 | MCP는 텍스트 검색-대체만 지원, 블록 ID 타겟팅 불가 |
| 페이지 아카이브(삭제) | MCP update-page에 archived 옵션 없음 |
| 대량 배치 처리 | Claude context 한계, 루프 자동화 불가 |
| 변경 감지 polling | MCP는 수동 요청만 가능 |
| DB 스키마 세밀 조작 | 속성 추가·삭제·순서 변경 |

---

## 설정

```python
NOTION_TOKEN = "${NOTION_TOKEN}  # 환경변수 NOTION_TOKEN 또는 .env 파일에 설정"
NOTION_VERSION = "2022-06-28"
```

토큰이 다르다면 사용자에게 확인 후 교체한다.

---

## 번들 스크립트

모든 작업은 `scripts/notion_api.py`를 활용한다.

```bash
# 실행 방법 (Windows PowerShell)
python -X utf8 .claude/skills/notion-api/scripts/notion_api.py <command> [options]
```

스크립트가 없거나 수정이 필요하면 직접 작성한다.

---

## 작업별 처리 방법

### 1. 블록 수정

```python
# scripts/notion_api.py 내 update_block() 또는 직접 API 호출
PATCH https://api.notion.com/v1/blocks/{block_id}
Body: {"paragraph": {"rich_text": [{"type": "text", "text": {"content": "새 내용"}}]}}
```

블록 ID는 `GET /blocks/{page_id}/children`으로 조회 후 사용한다.

### 2. 블록 삭제

```python
DELETE https://api.notion.com/v1/blocks/{block_id}
```

삭제 전 반드시 블록 ID를 확인한다.

### 3. 페이지 아카이브 (삭제)

```python
PATCH https://api.notion.com/v1/pages/{page_id}
Body: {"archived": true}
```

복원: `{"archived": false}`

### 4. 대량 배치 처리

`scripts/notion_api.py`의 `bulk_update()` 또는 `bulk_create()` 사용.
페이지 수가 많을 경우 100개 단위로 분할하여 처리한다.

### 5. 변경 감지

```python
# last_edited_time 기반 polling
GET /databases/{db_id}/query
Filter: {"property": "last_edited_time", "date": {"after": "<ISO datetime>"}}
```

결과를 Slack/이메일로 발송할 경우 해당 연동 스크립트를 별도 작성한다.

### 6. DB 스키마 조작

```python
PATCH https://api.notion.com/v1/databases/{database_id}
Body: {
  "properties": {
    "새 속성": {"rich_text": {}},          # 추가
    "기존 속성": {"name": "새 이름"},       # 이름 변경
    "삭제할 속성": null                     # 삭제
  }
}
```

---

## 실행 흐름

1. 사용자 요청을 위 6개 카테고리 중 하나로 분류한다.
2. `scripts/notion_api.py`를 사용하거나 필요 시 직접 API 호출 코드를 작성한다.
3. 실행 전 영향 범위(대상 페이지/블록 수)를 사용자에게 고지한다.
4. 삭제·아카이브처럼 되돌리기 어려운 작업은 실행 전 확인을 받는다.
5. 실행 결과를 요약해서 보고한다.

---

## 주의사항

- **블록/페이지 삭제는 되돌리기 어렵다.** 실행 전 반드시 확인.
- Rate limit: 초당 3요청. 대량 처리 시 `time.sleep(0.4)` 포함.
- Integration(JH_API)이 공유된 페이지/DB만 접근 가능.
- 권한 관리·실시간 협업·버전 히스토리는 API도 미지원 — Notion UI 사용.
