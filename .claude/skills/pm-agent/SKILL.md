---
name: pm-agent
description: >
  PM 에이전트 — Notion 5개 DB의 신규/미처리 항목을 감지하고 해당 서브 에이전트(task-request-agent, execution-agent, research-agent, knowledge-agent, schedule-agent)를 순차 호출해 자동 처리한다.
  "노션 DB 처리해줘", "새 항목 처리", "에이전트 실행", "PM 에이전트 돌려줘", "/pm-agent" 표현이 나오면 반드시 이 스킬을 사용한다.
argument-hint: [처리할 DB명(선택) | 전체]
allowed-tools: [mcp__claude_ai_Notion__notion-query-database-view, mcp__claude_ai_Notion__notion-fetch, mcp__claude_ai_Notion__notion-update-page, Bash, PowerShell]
---

# PM 에이전트 스킬

Notion 5개 DB를 순회하며 미처리 항목을 감지하고, DB 종류에 따라 서브 에이전트를 호출해 자동 처리합니다.

---

## 처리 대상 DB

| DB 이름 | DB URL | 신규 항목 기준 |
|---------|--------|--------------|
| 업무요청 DB | `https://app.notion.com/p/bf61a69aa0054e6fb0d7bd5ff254de77` | 상태 = `요청됨` |
| 실행업무 DB | `https://app.notion.com/p/981ae81b54da4ee3ac84951dce93844e` | 진행상태 = `할일` |
| 자료조사 DB | `https://app.notion.com/p/baff3d827f264f5e84fa58fd36ac18c5` | 상태 = `조사예정` |
| 업무지식 DB | `https://app.notion.com/p/e2338e0affcb4f9195910de77c0a65b8` | 에이전트처리 속성 없음 |
| 개인일정 DB | `https://app.notion.com/p/5db4c271e66141dba6699833ff10d4e6` | 에이전트처리 속성 없음 |

---

## Step 1: 신규 항목 감지

`mcp__claude_ai_Notion__notion-fetch` 또는 `mcp__claude_ai_Notion__notion-query-database-view`로 각 DB를 조회한다.

미처리 기준:
- 상태/진행상태가 초기값(`요청됨`, `할일`, `조사예정`)인 항목
- `에이전트처리` 속성이 없거나 비어 있는 항목
- 생성 후 처리 기록이 없는 항목

조회 결과를 리스트로 수집한다:
```
신규_항목_목록 = [
  { db: "업무요청", page_id: "...", 제목: "...", 속성: {...} },
  { db: "실행업무", page_id: "...", 제목: "...", 속성: {...} },
  ...
]
```

신규 항목이 없으면: "현재 처리할 신규 항목이 없습니다." 보고 후 종료.

---

## Step 2: DB별 서브 에이전트 라우팅

신규_항목_목록을 순회하며 DB에 따라 해당 서브 스킬을 호출한다:

| DB | 호출 스킬 |
|----|---------|
| 업무요청 DB | `/task-request-agent` |
| 실행업무 DB | `/execution-agent` |
| 자료조사 DB | `/research-agent` |
| 업무지식 DB | `/knowledge-agent` |
| 개인일정 DB | `/schedule-agent` |

각 서브 에이전트 호출 시 해당 페이지의 속성 데이터(제목, 날짜, 내용 등)를 전달한다.

### 서브 에이전트 호출 표시 규칙 (필수)

서브 에이전트를 호출하기 **직전**에 반드시 아래 형식으로 사용자에게 명시한다:

```
[서브 에이전트 호출] {스킬명} → {수행할 작업 한 줄 설명}
예) [서브 에이전트 호출] gws-slides → 회의자료 3페이지 생성 시작
예) [서브 에이전트 호출] Canva MCP (generate-design) → 배너 샘플 A 생성
예) [서브 에이전트 호출] task-request-agent → 이메일 초안 + 캘린더 등록
```

호출이 완료되면 결과를 한 줄로 보고한다:

```
[완료] {스킬명} → {결과 요약}
예) [완료] gws-slides → Google Slides 생성 완료 (링크: ...)
예) [완료] Canva MCP → 배너 후보 4건 생성 (샘플 A 후보 2건, 샘플 B 후보 2건)
```

> **배경**: 2026-06-28 실행 사례에서 gws-slides·Canva MCP 직접 호출 시 서브 에이전트 표시를 누락하여 사용자가 처리 흐름을 파악하지 못하는 문제가 발생. 이후 모든 서브 에이전트 호출에 이 규칙을 적용한다.

---

## Step 3: 처리 완료 표시

서브 에이전트가 처리를 완료하면 `mcp__claude_ai_Notion__notion-update-page`로 해당 Notion 페이지를 업데이트한다:

- 업무요청 DB: 상태 → `처리중` 또는 메모에 "에이전트처리: [날짜]" 추가
- 실행업무 DB: 비고에 "에이전트처리: [날짜]" 추가
- 자료조사 DB: 상태 → `조사완료` 또는 메모에 기록
- 업무지식 DB: 내용에 "에이전트처리: [날짜]" 추가
- 개인일정 DB: 메모에 "캘린더등록완료: [날짜]" 추가

---

## Step 4: 처리 결과 보고

전체 처리 완료 후 아래 형식으로 요약 보고:

```
[PM 에이전트 처리 완료]
- 총 처리 항목: N건
  ✓ 업무요청: N건 → 이메일 초안 + 캘린더 등록
  ✓ 실행업무: N건 → Google Tasks 생성
  ✓ 자료조사: N건 → 리서치 문서 생성
  ✓ 업무지식: N건 → 지식 문서 생성
  ✓ 개인일정: N건 → 캘린더 일정 등록
- 처리 실패: N건 (있을 경우 원인 기록)
```

---

## 주의사항

- 처리 순서: 업무요청 → 실행업무 → 자료조사 → 업무지식 → 개인일정 (우선순위 순)
- 서브 에이전트 호출 실패 시 해당 항목 건너뛰고 계속 진행, 실패 목록 별도 기록
- 한 번에 처리 가능한 최대 항목: 20건 (초과 시 우선순위 기준으로 상위 20건만 처리)
- 오늘 날짜 기준: `currentDate` 시스템 값 사용
