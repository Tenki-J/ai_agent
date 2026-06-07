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
├── 세계사_요약.txt
├── .claude/
│   ├── settings.local.json      # Permissions (gh CLI allowlist)
│   └── skills/
│       └── gh_cli/
│           └── SKILL.md         # gh CLI skill (local copy)
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
