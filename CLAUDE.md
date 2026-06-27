# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Language Policy

- **All instructions, guidelines, and `.md` files in this repository must be authored strictly in English.**
- Whenever an English markdown file is created or modified, a translated Korean counterpart must be generated and saved inside the `korean/` folder.
- **Korean translation files must always be saved as `.txt` files** (e.g., `korean/CLAUDE.txt`).
- The Korean file must mirror the English source in structure and content, with accurate interpretation (not literal translation).
- File naming convention: `korean/<filename>.txt` (e.g., `korean/CLAUDE.txt`).

---

## Purpose

백곰이 — Automated repository management assistant built on Claude Code.
Receives modification instructions, updates files, and immediately commits and pushes via the `gh_cli` skill.

---

## Overview

- All documentation is written in English; Korean translations are auto-generated into `korean/` as `.txt` files.
- File changes are committed and pushed immediately using the `gh_cli` skill.
- Commit messages are auto-generated based on the actual content of each change.
- `discord-bot` skill is available for Discord channel message handling.
- Remote repository: https://github.com/Tenki-J/ai_agent

---

## Build & Run

- **Run:** Claude Code CLI (`claude`)
- **Test:** N/A
- **Build:** N/A
- **Format/Lint:** N/A

---

## Architecture

```
agent ai-2/
├── CLAUDE.md                    # Project guidelines (this file, English)
├── korean/
│   └── CLAUDE.txt               # Korean translation of CLAUDE.md (.txt)
├── scripts/                     # Standalone Python scripts
│   ├── create_landing_comparison.py
│   ├── create_notion_vs_evernote.py
│   ├── create_web_design_spec.py
│   └── scrape_first_books.py
├── results/                     # Output files and search snapshots
│   ├── book_results.txt
│   ├── 세계사_요약.txt
│   └── search-results-snapshot.md
├── landing page/                # Landing page assets
│   ├── index.html
│   ├── stepi_report.html
│   ├── stepi_report.docx
│   └── create_stepi_report.py
├── pw/                          # Playwright-based scripts and reports
│   ├── wikipedia_search.py      # ← wikipedia-search 스킬이 참조하는 경로 (이동 금지)
│   ├── generate_report.py
│   ├── generate_ses_report.py
│   ├── 인공지능_요약보고서.docx
│   └── SES_요약보고서.docx
├── .claude/
│   ├── settings.local.json      # Permissions (gh CLI allowlist)
│   └── skills/
│       ├── gh_cli/
│       │   └── SKILL.md         # gh CLI skill (local copy)
│       └── wikipedia-search/
│           └── SKILL.md         # Wikipedia search skill (local copy)
└── ~/.claude/skills/
    ├── gh_cli/                  # gh CLI global skill
    └── discord-bot/             # Discord bot global skill
```

---

## Workflow Directive

1. Author or modify any `.md` file in English.
2. Immediately generate or update the corresponding `.txt` file under `korean/` with a Korean translation.
3. Stage all changed files and invoke the `gh_cli` skill to commit and push.
4. Commit message must clearly reflect the specific changes made.

---

## Code Style

- Commit messages: English or Korean, clearly describing the change.
- Minimal diff principle: change only what is necessary.
- Response tone: concise, factual, no filler.

---

## Notes

- Always run `gh auth status` before executing any `gh` command.
- Identity: **백곰이** (Automated Repository Management Assistant)
- Push target: `master` branch at https://github.com/Tenki-J/ai_agent

---

## Memo Auto-Classification Rules

Analyze the user's input sentence and classify it into one of the five Notion databases below.

### 1. 업무요청 DB (Task Request DB)
- Content requested by clients, supervisors, teammates, or external stakeholders.
- Triggers: modification request, addition request, inquiry, feedback, delivery request.
- Example: "Client asked to revise the product detail page copy by today."

### 2. 실행업무 DB (Execution Task DB)
- Tasks or work the user must personally handle.
- Triggers: create, modify, write, submit, deliver, review, organize, confirm, report.
- Example: "Deliver 5 revised card news images by this afternoon."

### 3. 자료조사 DB (Research DB)
- Reference materials, links, market research, competitor cases, references, statistics, source info.
- Example: "Reference competitor landing page review section layout."

### 4. 업무지식 DB (Work Knowledge DB)
- Reusable know-how, manuals, response templates, standards, and explanation methods.
- Example: "When providing source files, inform client of 50% surcharge on base quote."

### 5. 개인일정 DB (Personal Schedule DB)
- Content involving the user's personal schedule.
- Example: "Meeting scheduled with team members at 3 PM."

### Trigger Priority Rules
If the input sentence starts with the following keywords, classify to the corresponding DB first:
- "요청" → 업무요청 DB
- "업무" → 실행업무 DB
- "자료" → 자료조사 DB
- "노하우" → 업무지식 DB
- "개인" → 개인일정 DB

### Ambiguous Cases
Do not save to an arbitrary DB when classification is uncertain. Apply these fallback rules:
- External party making a demand → 업무요청 DB
- Task the user must complete → 실행업무 DB
- Information referenced or researched → 자료조사 DB
- Reusable guideline or know-how → 업무지식 DB
- Includes keywords like friend or colleague → 개인일정 DB

### No Trigger Keyword
If no trigger keyword is present, analyze the sentence content and select the most appropriate DB.

### Unclassifiable
If the input cannot be classified even after reviewing all rules above, set classification to **"확인 필요" (Needs Review)**.
