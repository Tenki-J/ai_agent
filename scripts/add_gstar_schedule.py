"""
지스타 2025 일정을 일정 관리 DB에 추가
- 지스타 개최 일정 (BTC/BTB)
- 입장권 예매 오픈 / 마감
- 개인 관람객 유의사항 항목
"""
import os
import sys, io, requests, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION, "Content-Type": "application/json"}

DB_ID = "38663685-d218-81aa-9ec4-eecd8a8e538a"


def post(path, body):
    r = requests.post(f"{BASE}{path}", headers=H, json=body)
    if r.status_code not in (200, 201):
        print(f"[FAIL] {r.status_code}: {r.text[:400]}")
        sys.exit(1)
    return r.json()

def ok(msg): print(f"[OK] {msg}")
def step(msg): print(f"\n── {msg}")


def add_entry(title, start, end=None, status="예정", priority="🔴 높음",
              categories=None, memo=""):
    props = {
        "일정 제목": {"title": [{"type": "text", "text": {"content": title}}]},
        "날짜": {"date": {"start": start, **({"end": end} if end else {})}},
        "상태": {"select": {"name": status}},
        "우선순위": {"select": {"name": priority}},
        "카테고리": {"multi_select": [{"name": c} for c in (categories or [])]},
        "메모": {"rich_text": [{"type": "text", "text": {"content": memo}}]},
    }
    result = post("/pages", {"parent": {"database_id": DB_ID}, "properties": props})
    ok(f"추가: {title}")
    time.sleep(0.4)
    return result


# ─────────────────────────────────────────────────────────
step("1. 지스타 2025 BTC 전시 (개인 관람 기간)")
add_entry(
    title="🎮 지스타 2025 BTC 전시 (개인 관람)",
    start="2025-11-13",
    end="2025-11-16",
    status="예정",
    priority="🔴 높음",
    categories=["개인", "기타"],
    memo=(
        "장소: 부산 벡스코(BEXCO) 제1전시장\n"
        "BTC(일반 관람): 11월 13일(목) ~ 16일(일) 4일간\n"
        "BTB(비즈니스): 11월 13일(목) ~ 15일(토) 3일간\n"
        "운영 시간: 오전 10시 ~ 오후 6시 (입장권 시간대 선택 필요)\n"
        "공식 홈페이지: www.gstar.or.kr"
    )
)

step("2. 입장권 예매 오픈일")
add_entry(
    title="🎟️ 지스타 2025 입장권 예매 오픈",
    start="2025-10-14",
    status="예정",
    priority="🔴 높음",
    categories=["개인"],
    memo=(
        "오픈 시각: 2025년 10월 14일(화) 오후 3시\n"
        "판매처: 예스24 단독 판매\n"
        "가격: 성인 15,000원 / 청소년 8,000원\n"
        "구매 한도: 1인 최대 2매\n"
        "입장 시간대: 10시 또는 12시 중 선택\n"
        "⚠️ 100% 온라인 예매만 가능 — 현장 구매 절대 불가"
    )
)

step("3. 입장권 예매 / 취소 마감 안내")
add_entry(
    title="⏰ 지스타 2025 입장권 취소·환불 마감",
    start="2025-11-12",
    status="예정",
    priority="🟡 보통",
    categories=["개인"],
    memo=(
        "예매 취소 마감: 관람 당일 하루 전 오후 17:00까지\n"
        "예매 판매 마감: 관람 당일 하루 전 24:00\n"
        "마감 이후 취소·환불 불가\n"
        "예: 11월 13일 관람 → 11월 12일 17:00까지 취소 가능\n"
        "⚠️ 취소 기한을 놓치지 않도록 미리 확인 필수"
    )
)

step("4. 개인 관람객 유의사항 — 준비물")
add_entry(
    title="🎒 지스타 관람 준비물 체크리스트",
    start="2025-11-13",
    end="2025-11-16",
    status="예정",
    priority="🟡 보통",
    categories=["개인"],
    memo=(
        "[필수]\n"
        "• 신분증: 주민등록증 또는 운전면허증 (본인 확인용, 미지참 시 입장 불가)\n"
        "• 스마트폰: QR코드 제시 → 현장에서 팔찌로 교환\n"
        "• 보조배터리: SNS 팔로우·이벤트 인증 등으로 배터리 소모 빠름\n"
        "\n[권장]\n"
        "• 크로스백 또는 작은 백팩 (양손 자유, 귀중품 보관)\n"
        "• 편한 신발 (하루 종일 서있거나 이동하는 일정)\n"
        "• 간단한 간식 및 생수 (전시장 내 매점 혼잡·가격 높음)\n"
        "• 핫팩 1~2개 (11월 부산 야외 대기 시 쌀쌀함)"
    )
)

step("5. 개인 관람객 유의사항 — 현장 팁")
add_entry(
    title="💡 지스타 관람 현장 팁",
    start="2025-11-13",
    end="2025-11-16",
    status="예정",
    priority="🟢 낮음",
    categories=["개인"],
    memo=(
        "[입장 시간 전략]\n"
        "• 10시 입장: 인기 부스 대기줄 선점 가능, 굿즈 소진 전 구매 유리\n"
        "• 12시 입장: 초반 혼잡 회피, 다소 여유로운 관람 가능\n"
        "• 목·금요일이 토·일요일보다 혼잡도 낮음 → 평일 방문 추천\n"
        "\n[혼잡 시간대 주의]\n"
        "• 오전 개장 직후 / 오후 2~4시 → 대기줄 최장\n"
        "• 인기 부스는 폐장 직전 타임 狙\n"
        "\n[관람 규정]\n"
        "• 위험물 반입 금지 (날카로운 물건, 대형 소품 등)\n"
        "• 공공 법규 위반 코스튬 착용 시 입장 제한\n"
        "• 일부 부스는 별도 사전 예약 필요 (사전 확인 요)\n"
        "\n[교통 안내]\n"
        "• 부산 지하철 2호선 센텀시티역 하차 → 벡스코 도보 5분\n"
        "• 행사 기간 주차 혼잡 → 대중교통 적극 권장"
    )
)

step("6. 지스타 2025 관람 당일 일정 (예시)")
add_entry(
    title="📅 지스타 2025 관람 계획 (직접 작성)",
    start="2025-11-15",
    status="예정",
    priority="🟡 보통",
    categories=["개인"],
    memo=(
        "관람 희망일: 11월 15일(토) — 필요 시 날짜 변경\n"
        "입장 시간대: 10시 / 12시 중 선택 예정\n"
        "목표 부스: (입력 예정)\n"
        "동행 인원: (입력 예정)\n"
        "\n[TO-DO]\n"
        "□ 10월 14일 오후 3시 예매 알림 설정\n"
        "□ 입장권 예매 완료 후 QR 저장\n"
        "□ 당일 신분증 지참 확인\n"
        "□ 교통 편 사전 예약 (KTX 등)"
    )
)

print(f"""
{'='*55}
  지스타 2025 일정 추가 완료
{'='*55}
  추가된 항목 6건:
  1. 🎮 BTC 전시 기간   2025-11-13 ~ 11-16
  2. 🎟️ 입장권 예매 오픈 2025-10-14 오후 3시
  3. ⏰ 취소·환불 마감  관람 전일 17:00
  4. 🎒 준비물 체크리스트
  5. 💡 현장 팁
  6. 📅 관람 계획 (사용자 직접 작성용)
""")
