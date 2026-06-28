---
name: task-request-agent
description: >
  업무요청 에이전트 — Notion 업무요청 DB의 신규 항목을 받아 클라이언트 답변 이메일 초안(Gmail)을 생성하고 마감일을 Google Calendar에 등록한다.
  PM 에이전트에 의해 자동 호출되거나, "/task-request-agent [페이지정보]" 형식으로 단독 실행 가능.
argument-hint: [Notion 페이지 ID 또는 속성 데이터]
allowed-tools: [mcp__claude_ai_Gmail__create_draft, mcp__claude_ai_Gmail__list_labels, mcp__claude_ai_Google_Calendar__create_event, mcp__claude_ai_Notion__notion-update-page, mcp__claude_ai_Notion__notion-fetch]
---

# 업무요청 에이전트 스킬

Notion 업무요청 DB의 신규 항목을 분석해 Gmail 답변 초안 작성 + Google Calendar 마감일 등록을 수행합니다.

---

## 입력 데이터

PM 에이전트로부터 받는 항목 구조:
```
{
  "page_id": "notion-page-id",
  "요청명": "클라이언트가 요청한 내용",
  "마감일": "2026-06-30",      // 없을 수 있음
  "요청자": "홍길동",            // 없을 수 있음
  "메모": "원문 전체",
  "카테고리": "수정/추가/문의"   // 없을 수 있음
}
```

단독 실행 시 args로 위 정보를 직접 받거나 Notion 페이지 ID만 받아 fetch.

---

## Step 1: 데이터 확인

입력 데이터에서 다음 정보를 추출:
- **요청 내용**: 무엇을 해달라는 요청인지
- **요청자**: 이름/회사/연락처 (있으면)
- **마감일**: 언제까지 해야 하는지 (없으면 오늘 기준 +3일 기본값)
- **카테고리**: 수정/추가/문의/확인 등

---

## Step 2: Gmail 답변 초안 작성

`mcp__claude_ai_Gmail__create_draft`를 사용해 답변 초안을 생성한다.

**초안 작성 규칙:**
- To: 요청자 이메일 (없으면 비워둠)
- Subject: `[답변] {요청명 요약}`
- Body 구성:
  ```
  안녕하세요,
  
  요청하신 [{요청명}] 관련하여 확인 후 회신드립니다.
  
  [처리 방향 또는 검토 중 표현 — 요청 내용 기반으로 작성]
  
  마감일({마감일})까지 처리해드리겠습니다.
  
  감사합니다.
  ```
- 요청 유형에 맞게 내용 조정:
  - 수정 요청 → "수정 사항 검토 후 반영하겠습니다"
  - 문의 → "확인 후 빠른 시간 내 답변드리겠습니다"
  - 추가 요청 → "추가 작업 일정 협의 후 진행하겠습니다"

---

## Step 3: Google Calendar 마감일 등록

`mcp__claude_ai_Google_Calendar__create_event`로 마감일을 캘린더에 등록한다.

**이벤트 설정:**
- 제목: `[업무요청] {요청명}`
- 날짜: 마감일 (종일 이벤트)
- 설명: `요청자: {요청자}\n요청내용: {메모}\nNotion: {page_url}`
- 캘린더: 기본 캘린더
- 알림: 마감 1일 전 오전 9시

---

## Step 4: Notion 페이지 업데이트

`mcp__claude_ai_Notion__notion-update-page`로 처리 결과를 Notion에 기록한다:
- 상태: `처리중`
- 메모에 추가: "에이전트처리: {오늘날짜} / Gmail초안생성 / 캘린더등록완료"

---

## Step 5: 결과 보고

```
[업무요청 에이전트 처리 완료]
- 요청명: {요청명}
- Gmail 초안: 생성 완료 (수신자: {요청자 또는 "미지정"})
- 캘린더 등록: {마감일} "{제목}"
- Notion 업데이트: 상태 → 처리중
```

---

## 주의사항

- 이메일 초안은 자동 발송하지 않음 — 사용자가 직접 검토 후 발송
- 요청자 이메일 없는 경우 To 빈칸 유지, 사용자가 채워서 발송
- 마감일 없을 경우 오늘 + 3일을 기본 마감일로 사용하고 사용자에게 알림
