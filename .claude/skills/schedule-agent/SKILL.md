---
name: schedule-agent
description: >
  일정관리 에이전트 — Notion 개인일정 DB의 신규 항목을 받아 Google Calendar에 일정을 등록하고, 미팅/회의 유형이면 Google Meet 링크도 생성한다.
  PM 에이전트에 의해 자동 호출되거나, "/schedule-agent [페이지정보]" 형식으로 단독 실행 가능.
argument-hint: [Notion 페이지 ID 또는 일정 정보]
allowed-tools: [mcp__claude_ai_Google_Calendar__create_event, mcp__claude_ai_Google_Calendar__list_calendars, mcp__claude_ai_Google_Calendar__suggest_time, mcp__claude_ai_Notion__notion-update-page, mcp__claude_ai_Notion__notion-fetch]
---

# 일정관리 에이전트 스킬

Notion 개인일정 DB의 신규 항목을 분석해 Google Calendar 등록 + 필요 시 Google Meet 링크 생성을 수행합니다.

---

## 입력 데이터

PM 에이전트로부터 받는 항목 구조:
```
{
  "page_id": "notion-page-id",
  "일정명": "이벤트 이름",
  "일정": "2026-07-01T15:00",  // 날짜 또는 날짜+시간
  "장소": "서울 강남구 ...",    // 없을 수 있음
  "메모": "원문 전체",
  "유형": "미팅/업무/개인/교육/기타"
}
```

---

## Step 1: 일정 정보 파싱

입력에서 추출:
- **일정명**: 캘린더 이벤트 제목
- **날짜/시간**: ISO 형식으로 변환 (시간 없으면 종일 이벤트)
- **장소**: 오프라인 장소 또는 온라인 여부
- **유형**: 미팅/회의/교육 → Meet 링크 생성 대상
- **참석자**: 메모에 사람 이름이나 "팀", "클라이언트" 언급되면 기록

---

## Step 2: 시간 충돌 확인

`mcp__claude_ai_Google_Calendar__list_calendars`로 해당 날짜 기존 일정 확인.

충돌 발견 시:
- 사용자에게 알림: "해당 시간에 [{기존 일정명}]이 있습니다. 그대로 등록할까요?"
- 사용자 확인 후 진행

---

## Step 3: Google Calendar 이벤트 생성

`mcp__claude_ai_Google_Calendar__create_event`로 일정 등록.

**이벤트 설정:**
- 제목: `{일정명}`
- 시작: `{날짜/시간}`
- 종료: 시간 있으면 시작 + 1시간 기본 / 종일 이벤트면 하루
- 장소: `{장소}` (있으면)
- 설명: `{메모}\n유형: {유형}\nNotion: {page_url}`
- 알림 설정:
  - 종일 이벤트: 전날 오전 9시
  - 시간 지정 이벤트: 30분 전 + 10분 전

---

## Step 4: Google Meet 링크 생성 (조건부)

유형이 `미팅` / `회의` / `교육` 이거나 메모에 "온라인", "비대면", "Zoom", "Meet" 언급 시:

`gws-meet` 스킬을 호출해 Google Meet 링크를 생성하고 캘린더 이벤트에 포함.

또는 `mcp__claude_ai_Google_Calendar__create_event`의 conferenceData 옵션을 활용해 Meet 링크를 이벤트에 직접 포함.

---

## Step 5: Notion 페이지 업데이트

`mcp__claude_ai_Notion__notion-update-page`로 처리 기록:
- 메모에 추가: "에이전트처리: {오늘날짜} / 캘린더등록완료{Meet링크있으면: / Meet: {url}}"

---

## Step 6: 결과 보고

```
[일정관리 에이전트 처리 완료]
- 일정명: {일정명}
- 날짜/시간: {등록된 날짜/시간}
- 장소: {장소 또는 "온라인"}
- Google Meet: {링크 또는 "해당없음"}
- 알림: {설정된 알림 시간}
- Notion 업데이트: 완료
```

---

## 주의사항

- 시간이 과거인 경우(이미 지난 일정) 등록 여부를 사용자에게 확인
- 참석자 이름만 있고 이메일을 모를 경우 초대는 생략하고 이벤트 설명에 참석자 기록
- 반복 일정(매주, 매월)은 메모에 "반복" 언급 시 사용자에게 반복 주기 확인 후 설정
