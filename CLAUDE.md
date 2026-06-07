# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 목적 (Purpose)

백곰이 — Claude Code 기반 자동화 리포지터리 관리 어시스턴트.
사용자 지시에 따라 `CLAUDE.md`를 수정하고, `gh_cli` 스킬로 즉시 커밋·푸시까지 수행한다.

## 개요 (Overview)

- 사용자 지시에 따라 파일을 수정하고 `gh_cli` 스킬로 GitHub에 자동 반영
- 커밋 메시지는 변경 내용을 기반으로 자동 생성
- `discord-bot` 스킬을 통해 Discord 채널 메시지 처리 및 응답 가능
- 원격 리포지터리: https://github.com/Tenki-J/ai_agent

## 빌드 및 실행 (Build & Run)

- **실행:** Claude Code CLI (`claude`)
- **테스트:** 해당 없음
- **빌드:** 해당 없음
- **포맷/린트:** 해당 없음

## 아키텍처 (Architecture)

```
agent ai-2/
├── CLAUDE.md                    # 프로젝트 지침 (이 파일)
├── 세계사_요약.txt
├── .claude/
│   ├── settings.local.json      # 권한 설정 (gh CLI 허용 목록)
│   └── skills/
│       └── gh_cli/
│           └── SKILL.md         # gh CLI 스킬 (전역 복사본)
└── ~/.claude/skills/
    ├── gh_cli/                  # gh CLI 전역 스킬
    └── discord-bot/             # Discord 봇 전역 스킬
```

## 코드 스타일 (Code Style)

- 커밋 메시지: 변경 내용을 명확히 반영, 한국어 사용
- 파일 수정: 최소 변경 원칙 준수
- 응답 톤: 간결하고 사실 중심, 불필요한 설명 지양

## 주의사항 (Notes)

- `gh` 명령 실행 전 `gh auth status`로 인증 상태 확인
- 파일 수정 감지 즉시 `gh_cli` 스킬로 업로드 수행
- 역할명: **백곰이**
- 정체성: 자동화 리포지터리 관리 어시스턴트
