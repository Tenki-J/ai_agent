---
name: research-agent
description: >
  자료조사 에이전트 — Notion 자료조사 DB의 신규 항목을 받아 리서치를 수행하고 Google Docs에 요약 문서를 생성한 후 Google Drive에 저장한다.
  PM 에이전트에 의해 자동 호출되거나, "/research-agent [조사주제]" 형식으로 단독 실행 가능.
argument-hint: [Notion 페이지 ID 또는 조사 주제]
allowed-tools: [mcp__claude_ai_Google_Drive__create_file, mcp__claude_ai_Google_Drive__search_files, mcp__claude_ai_Notion__notion-update-page, mcp__claude_ai_Notion__notion-fetch, WebSearch, WebFetch]
---

# 자료조사 에이전트 스킬

Notion 자료조사 DB의 신규 항목을 분석해 리서치 수행 → Docs 요약 문서 생성 → Drive 저장을 수행합니다.

---

## 입력 데이터

PM 에이전트로부터 받는 항목 구조:
```
{
  "page_id": "notion-page-id",
  "조사 주제": "조사할 내용",
  "출처": "https://...",   // URL이 있을 경우
  "요약": "원문 전체",
  "분류": "경쟁사/시장조사/레퍼런스/통계" // 없을 수 있음
}
```

---

## Step 1: 조사 범위 판단

입력 분석:
- **조사 주제** 파악
- **출처 URL 있음** → 해당 URL 내용 fetch 후 요약
- **출처 URL 없음** → 웹 검색으로 자료 수집
- **분류** 파악 → 문서 구조 결정

---

## Step 2: 리서치 수행

### Case A: 출처 URL 있는 경우
`WebFetch`로 URL 콘텐츠를 가져와 핵심 내용을 추출한다:
- 페이지 제목, 주요 내용, 핵심 수치/데이터 정리
- 원문 요약 (500자 이내)

### Case B: 출처 URL 없는 경우
`WebSearch` 또는 `deep-research` 스킬을 호출해 조사 주제 검색:
- 검색 키워드: `{조사 주제}` + 관련 키워드
- 상위 3~5개 결과 수집
- 각 결과 핵심 내용 요약

### 공통: wikipedia-search 스킬
개념/용어 설명이 필요한 경우 `wikipedia-search` 스킬도 활용.

---

## Step 3: Google Docs 요약 문서 생성

`gws-docs` 스킬을 호출해 리서치 결과 문서를 생성한다.

**문서 구조:**
```
제목: [자료조사] {조사 주제}

■ 조사 개요
- 주제: {조사 주제}
- 분류: {분류}
- 조사일: {오늘날짜}
- 출처: {URL 또는 "웹 검색"}

■ 핵심 요약
{리서치 결과 요약 — 300~500자}

■ 세부 내용
{수집한 내용 정리 — 항목별 bullet}

■ 주요 수치 / 데이터
{수치나 통계가 있으면 표 형식으로}

■ 시사점 / 활용 방안
{실무에 어떻게 활용할 수 있는지 1~3줄}

■ 참고 링크
- {출처 URL들}
- Notion 원본: {page_url}
```

---

## Step 4: Google Drive 저장

`gws-drive` 스킬로 생성된 문서를 Drive "자료조사" 폴더에 저장한다:
- 폴더명: "자료조사" (없으면 생성)
- 파일명: `[{분류}] {조사 주제}_{날짜}.docx`

---

## Step 5: Notion 페이지 업데이트

`mcp__claude_ai_Notion__notion-update-page`로 처리 결과 기록:
- 상태: `조사완료`
- 요약 속성: 리서치 핵심 요약 (200자 이내)
- 메모에 추가: "에이전트처리: {오늘날짜} / Docs링크: {google_docs_url}"

---

## Step 6: 결과 보고

```
[자료조사 에이전트 처리 완료]
- 조사 주제: {조사 주제}
- 수집 출처: {N}건
- Docs 문서: "{문서 제목}" 생성 완료
- Drive 저장: 자료조사/{파일명}
- Notion 업데이트: 상태 → 조사완료
```

---

## 주의사항

- 조사 결과가 불충분하면 사용자에게 추가 키워드나 출처를 요청
- 개인정보나 민감 정보는 문서에 포함하지 않음
- 웹 검색 결과는 사실 확인 후 요약 (출처 명시 필수)
