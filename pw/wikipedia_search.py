# -*- coding: utf-8 -*-
"""
Wikipedia 검색 자동화 스크립트
- Playwright로 위키백과 접속
- 검색어 입력 → 첫 번째 결과 페이지 이동
- 본문 내용 추출 → 요약 반환
"""

import sys
import re
import textwrap
from playwright.sync_api import sync_playwright


# ── 설정 ──────────────────────────────────────────────
WIKIPEDIA_URL = "https://ko.wikipedia.org"
MAX_PARAGRAPHS = 5      # 요약에 포함할 최대 문단 수
MAX_CHARS     = 800     # 요약 최대 글자 수
HEADLESS      = True    # False 로 바꾸면 브라우저 창이 보임


# ── 핵심 함수 ─────────────────────────────────────────
def search_and_summarize(keyword: str) -> dict:
    """
    keyword 를 위키백과에서 검색하고 첫 번째 결과를 요약한다.

    Returns:
        {
          "keyword": str,
          "title": str,
          "url": str,
          "summary": str,
          "sections": list[str]   # 목차 항목
        }
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        # 1) 위키백과 접속
        print(f"[1/4] 위키백과 접속 중...")
        page.goto(WIKIPEDIA_URL, wait_until="networkidle")

        # 2) 검색어 입력 & 검색
        print(f"[2/4] 검색어 입력: '{keyword}'")
        search_box = page.locator('input[type="search"], #searchInput, [name="search"]').first
        search_box.fill(keyword)
        search_box.press("Enter")
        page.wait_for_load_state("networkidle")

        # 검색 결과 페이지인지 문서 페이지인지 판단
        current_url = page.url
        print(f"[3/4] 이동된 URL: {current_url}")

        # 검색 결과 목록 페이지로 갔을 경우 첫 번째 결과 클릭
        if "Special:Search" in current_url or "special:search" in current_url.lower():
            first_result = page.locator(".mw-search-result-heading a").first
            first_result.wait_for(timeout=5000)
            article_title = first_result.inner_text().strip()
            first_result.click()
            page.wait_for_load_state("networkidle")
        else:
            # 직접 문서 페이지로 이동된 경우
            article_title = page.title().split(" - ")[0].strip()

        final_url = page.url
        print(f"[4/4] 문서 페이지 도착: {final_url}")

        # 4) 본문 추출
        paragraphs_raw = page.locator("#bodyContent p").all_inner_texts()

        # 빈 줄·각주 기호 제거, 의미 있는 문단만 필터
        paragraphs = []
        for p in paragraphs_raw:
            cleaned = re.sub(r'\[\d+\]', '', p).strip()   # [1] [2] 각주 제거
            cleaned = re.sub(r'\s+', ' ', cleaned)         # 연속 공백 정리
            if len(cleaned) > 30:                          # 너무 짧은 줄 제외
                paragraphs.append(cleaned)
            if len(paragraphs) >= MAX_PARAGRAPHS:
                break

        summary_text = "\n\n".join(paragraphs)
        if len(summary_text) > MAX_CHARS:
            summary_text = summary_text[:MAX_CHARS].rsplit(' ', 1)[0] + "..."

        # 목차 추출 (Vector 2022 스킨 기준)
        toc_items = page.locator(".vector-toc-text, .toctext").all_inner_texts()
        toc_clean  = [t.strip() for t in toc_items if t.strip()]

        browser.close()

        return {
            "keyword" : keyword,
            "title"   : article_title,
            "url"     : final_url,
            "summary" : summary_text,
            "sections": toc_clean,
        }


def print_result(result: dict):
    """결과를 보기 좋게 출력"""
    sep = "=" * 60
    print()
    print(sep)
    print(f"  검색어  : {result['keyword']}")
    print(f"  문서 제목: {result['title']}")
    print(f"  URL     : {result['url']}")
    print(sep)

    print("\n[ 요약 ]")
    for line in result["summary"].split("\n\n"):
        print(textwrap.fill(line, width=70))
        print()

    if result["sections"]:
        print("[ 목차 ]")
        for i, sec in enumerate(result["sections"], 1):
            print(f"  {i:>2}. {sec}")
    print(sep)


# ── 실행 진입점 ───────────────────────────────────────
if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "인공지능"
    try:
        result = search_and_summarize(keyword)
        print_result(result)
    except Exception as e:
        print(f"\n[오류] {e}", file=sys.stderr)
        sys.exit(1)
