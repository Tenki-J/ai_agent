---
name: gh_cli
description: GitHub CLI(gh) 명령어를 활용해 GitHub 작업을 수행하는 스킬. 이슈, PR, 리포지터리, GitHub Actions, 릴리즈, Gist, 코드 검색 등 gh CLI로 할 수 있는 모든 작업에 사용한다. 사용자가 "PR 만들어", "이슈 올려", "gh로 해줘", "리포 만들어", "워크플로우 실행해", "릴리즈 만들어", "코드 검색해줘", "GitHub에서 ~해줘" 등의 표현을 쓰면 반드시 이 스킬을 사용한다.
---

# gh CLI 스킬

GitHub CLI(`gh`)로 GitHub의 모든 기능을 터미널에서 수행한다.

---

## 인증 확인

작업 시작 전에 항상 인증 상태를 확인한다.

```bash
gh auth status
```

인증이 안 된 경우 사용자에게 `gh auth login` 실행을 안내한다.

---

## 리포지터리 (repo)

```bash
# 현재 리포 정보
gh repo view
gh repo view --web                        # 브라우저에서 열기

# 리포 생성 / 클론 / 포크
gh repo create <name> --public            # 공개 리포 생성
gh repo create <name> --private           # 비공개 리포 생성
gh repo clone <owner/repo>
gh repo fork <owner/repo> --clone

# 리포 목록 / 삭제
gh repo list <owner>
gh repo delete <owner/repo>

# 리포 설정 편집
gh repo edit --description "설명" --homepage "https://..."
gh repo edit --enable-issues --enable-wiki
```

---

## 이슈 (issue)

```bash
# 목록 / 상세
gh issue list
gh issue list --assignee @me --state open
gh issue list --label "bug" --limit 20
gh issue view <number>
gh issue view <number> --web

# 생성 / 수정 / 닫기
gh issue create --title "제목" --body "내용"
gh issue create --title "제목" --label "bug" --assignee "@me"
gh issue edit <number> --title "새 제목" --add-label "enhancement"
gh issue close <number>
gh issue reopen <number>

# 댓글
gh issue comment <number> --body "댓글 내용"

# 검색
gh issue list --search "keyword"
```

---

## 풀 리퀘스트 (pr)

```bash
# 목록 / 상세
gh pr list
gh pr list --state merged
gh pr view <number>
gh pr view <number> --web

# 생성
gh pr create --title "제목" --body "내용"
gh pr create --base main --head feature-branch --title "제목"
gh pr create --draft                      # 드래프트 PR

# 리뷰 / 머지 / 닫기
gh pr review <number> --approve
gh pr review <number> --request-changes --body "수정 필요"
gh pr merge <number> --merge              # 일반 머지
gh pr merge <number> --squash             # 스쿼시 머지
gh pr merge <number> --rebase             # 리베이스 머지
gh pr close <number>

# 체크아웃 / diff
gh pr checkout <number>
gh pr diff <number>

# 댓글
gh pr comment <number> --body "댓글"

# 레이블 / 리뷰어 지정
gh pr edit <number> --add-label "ready" --add-reviewer "username"

# 준비 완료 (드래프트 → 정식)
gh pr ready <number>
```

---

## GitHub Actions (workflow / run)

```bash
# 워크플로우 목록
gh workflow list
gh workflow view <name-or-id>

# 워크플로우 실행 / 비활성화
gh workflow run <workflow.yml>
gh workflow run <workflow.yml> --ref main -f key=value
gh workflow disable <name>
gh workflow enable <name>

# 실행 목록 / 상세 / 모니터링
gh run list
gh run list --workflow <workflow.yml> --limit 10
gh run view <run-id>
gh run view <run-id> --log               # 로그 보기
gh run watch <run-id>                    # 실시간 모니터링

# 재실행 / 취소
gh run rerun <run-id>
gh run cancel <run-id>

# 아티팩트 다운로드
gh run download <run-id>
gh run download <run-id> --name <artifact-name>
```

---

## 릴리즈 (release)

```bash
# 목록 / 상세
gh release list
gh release view <tag>
gh release view <tag> --web

# 생성
gh release create v1.0.0 --title "v1.0.0" --notes "릴리즈 노트"
gh release create v1.0.0 --generate-notes  # 자동 릴리즈 노트
gh release create v1.0.0 --draft           # 드래프트 릴리즈
gh release create v1.0.0 ./dist/*.zip      # 파일 첨부

# 수정 / 삭제
gh release edit <tag> --title "새 제목"
gh release delete <tag>

# 자산 업로드 / 다운로드
gh release upload <tag> ./file.zip
gh release download <tag>
```

---

## Gist

```bash
# 생성 / 목록 / 보기
gh gist create file.txt --desc "설명" --public
gh gist create file.txt --secret
gh gist list
gh gist view <gist-id>
gh gist view <gist-id> --web

# 수정 / 삭제
gh gist edit <gist-id>
gh gist delete <gist-id>

# 클론
gh gist clone <gist-id>
```

---

## 코드 / 리포 / 이슈 검색 (search)

```bash
# 리포 검색
gh search repos "키워드"
gh search repos "topic:machine-learning" --limit 20 --sort stars

# 이슈 / PR 검색
gh search issues "버그" --repo owner/repo
gh search prs "feat" --state open

# 코드 검색
gh search code "함수명" --repo owner/repo
```

---

## 브랜치 및 커밋

```bash
# 브랜치 목록 (API 활용)
gh api repos/{owner}/{repo}/branches

# 커밋 목록
gh api repos/{owner}/{repo}/commits --jq '.[].commit.message'
```

---

## API 직접 호출

`gh api`로 GitHub REST/GraphQL API를 직접 호출할 수 있다.

```bash
# REST API
gh api repos/{owner}/{repo}
gh api repos/{owner}/{repo}/issues --jq '.[].title'
gh api -X POST repos/{owner}/{repo}/issues \
  --field title="제목" --field body="내용"

# GraphQL
gh api graphql -f query='
  query {
    viewer { login }
  }
'

# 페이지네이션
gh api repos/{owner}/{repo}/issues --paginate
```

---

## 알림 및 상태

```bash
gh status                                 # 내 알림, 멘션, PR 확인
gh api notifications                      # 미읽 알림
gh api notifications -X PUT --input - <<< '{}' # 전체 읽음 처리
```

---

## 환경 변수 및 Secrets

```bash
# Secrets (리포 레벨)
gh secret list
gh secret set MY_SECRET
gh secret delete MY_SECRET

# Variables
gh variable list
gh variable set MY_VAR --body "값"
gh variable delete MY_VAR
```

---

## 유용한 패턴

### 출력 포맷
```bash
gh issue list --json number,title,state
gh pr list --json number,title --jq '.[].title'
```

### 현재 리포 owner/repo 자동 참조
`gh` 명령은 git remote origin을 자동 인식한다. 별도로 `--repo owner/repo`를 지정하지 않아도 현재 디렉터리의 리포에 작동한다.

### 도움말
```bash
gh <command> --help           # 명령어별 상세 옵션 확인
gh help
```
