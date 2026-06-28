---
name: execution-agent
description: >
  실행업무 에이전트 — Notion 실행업무 DB의 신규 항목을 받아 Google Tasks에 작업을 등록하고, 필요 시 Google Docs 작업 문서 및 Google Sheets 진행 시트를 생성한다.
  PM 에이전트에 의해 자동 호출되거나, "/execution-agent [페이지정보]" 형식으로 단독 실행 가능.
argument-hint: [Notion 페이지 ID 또는 속성 데이터]
allowed-tools: [mcp__claude_ai_Google_Calendar__create_event, mcp__claude_ai_Notion__notion-update-page, mcp__claude_ai_Notion__notion-fetch, mcp__claude_ai_Google_Drive__create_file]
---

# 실행업무 에이전트 스킬

Notion 실행업무 DB의 신규 항목을 분석해 Google Tasks 등록 + 필요 시 Docs/Sheets 생성을 수행합니다.

---

## 입력 데이터

PM 에이전트로부터 받는 항목 구조:
```
{
  "page_id": "notion-page-id",
  "업무명": "처리해야 할 작업 제목",
  "마감일": "2026-07-01",      // 없을 수 있음
  "비고": "원문 전체",
  "업무 유형": "제작/수정/검토/보고" // 없을 수 있음
}
```

---

## Step 1: 데이터 분석

입력에서 추출:
- **업무명**: 해야 할 작업 이름
- **마감일**: 기한 (없으면 오늘 + 2일)
- **업무 유형**: 제작/수정/검토/보고/기타
- **복잡도 판단**: 비고 내용이 300자 초과 또는 단계가 여러 개이면 "Docs 필요"로 분류

---

## Step 2: Google Tasks 등록

`gws-tasks` 스킬을 호출해 Google Tasks에 작업을 추가한다.

**Tasks 항목 설정:**
- 제목: `{업무명}`
- 기한: `{마감일}`
- 메모: `{비고 요약 (100자 이내)}\nNotion: {page_url}`
- 목록: "업무" 목록 (없으면 기본 목록)

---

## Step 3: 문서 생성 (조건부)

업무 유형이 "제작" 또는 복잡도 높음인 경우 `gws-docs` 스킬을 호출해 작업 문서를 생성한다.

**Docs 문서 구조:**
```
제목: [실행업무] {업무명}

1. 업무 개요
   - 업무명: {업무명}
   - 마감일: {마감일}
   - 유형: {업무 유형}

2. 작업 내용
   {비고 전문}

3. 진행 체크리스트
   □ 작업 시작
   □ 중간 검토
   □ 최종 완료
   □ 전달/제출

4. 참고사항
   - Notion 링크: {page_url}
   - 생성일: {오늘날짜}
```

생성 후 Google Drive "업무문서" 폴더에 저장 (`gws-drive` 스킬 활용).

---

## Step 4: 마감 캘린더 등록 (조건부)

마감일이 명시된 경우 `gws-calendar` 스킬로 캘린더에도 등록한다:
- 제목: `[마감] {업무명}`
- 날짜: 마감일 (종일)
- 알림: 전날 오전 9시

---

## Step 5: Notion 페이지 업데이트

처리 완료 후 Notion 업데이트:
- 비고에 추가: "에이전트처리: {오늘날짜} / Tasks등록 / {Docs생성 여부}"

---

## Step 6: 결과 보고

```
[실행업무 에이전트 처리 완료]
- 업무명: {업무명}
- Google Tasks: 등록 완료 (마감: {마감일})
- Docs 문서: {생성됨 / 해당없음}
- 캘린더: {등록됨 / 해당없음}
- Notion 업데이트: 완료
```

---

## 주의사항

- Docs 자동 생성은 업무 유형이 "제작"이거나 비고가 길 때만 수행 (단순 체크 업무는 Tasks만 등록)
- 마감일 없을 경우 오늘 + 2일을 기본값으로 사용하고 Tasks 메모에 "(기본 마감일 적용)" 표시
