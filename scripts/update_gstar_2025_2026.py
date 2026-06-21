"""
1. 2025년 지스타 항목 6개 → 상태 '완료'로 일괄 변경
2. 2026년 지스타 항목 추가
"""
import os
import sys, io, requests, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION, "Content-Type": "application/json"}
DB_ID = "38663685-d218-81aa-9ec4-eecd8a8e538a"

IDS_2025 = [
    ("38663685-d218-819a-84f2-f3d718df13b6", "🎮 지스타 2025 BTC 전시 (개인 관람)"),
    ("38663685-d218-81ca-88e9-d8850ac8db9a", "🎟️ 지스타 2025 입장권 예매 오픈"),
    ("38663685-d218-8118-8c0d-d08b732a2b0e", "⏰ 지스타 2025 입장권 취소·환불 마감"),
    ("38663685-d218-81e9-a72e-ee9c8cea89b4", "🎒 지스타 관람 준비물 체크리스트"),
    ("38663685-d218-814c-bbf1-ca1cf5915a07", "💡 지스타 관람 현장 팁"),
    ("38663685-d218-81c7-a17b-cb80c2e0d84a", "📅 지스타 2025 관람 계획 (직접 작성)"),
]

def ok(msg):   print(f"  [OK] {msg}")
def step(msg): print(f"\n── {msg}")

def patch(path, body):
    r = requests.patch(f"{BASE}{path}", headers=H, json=body)
    if r.status_code not in (200, 201):
        print(f"  [FAIL] {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    return r.json()

def post(path, body):
    r = requests.post(f"{BASE}{path}", headers=H, json=body)
    if r.status_code not in (200, 201):
        print(f"  [FAIL] {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    return r.json()

def add_entry(title, start, end=None, status="예정", priority="🔴 높음",
              categories=None, memo=""):
    props = {
        "일정 제목": {"title": [{"type": "text", "text": {"content": title}}]},
        "날짜":     {"date": {"start": start, **({"end": end} if end else {})}},
        "상태":     {"select": {"name": status}},
        "우선순위": {"select": {"name": priority}},
        "카테고리": {"multi_select": [{"name": c} for c in (categories or [])]},
        "메모":     {"rich_text": [{"type": "text", "text": {"content": memo}}]},
    }
    post("/pages", {"parent": {"database_id": DB_ID}, "properties": props})
    ok(f"추가: {title}")
    time.sleep(0.4)


# ── STEP 1. 2025년 항목 → '완료' 일괄 변경 ───────────────
step("STEP 1. 2025년 지스타 항목 상태 → '완료' 일괄 변경")
for pid, title in IDS_2025:
    patch(f"/pages/{pid}", {"properties": {"상태": {"select": {"name": "완료"}}}})
    ok(f"완료 처리: {title[:35]}")
    time.sleep(0.4)


# ── STEP 2. 2026년 항목 추가 ─────────────────────────────
step("STEP 2. 지스타 2026 일정 추가")

# ① 개최 일정 (BTC 전시)
add_entry(
    title="🎮 지스타 2026 BTC 전시 (개인 관람)",
    start="2026-11-19",
    end="2026-11-22",
    status="예정",
    priority="🔴 높음",
    categories=["개인", "기타"],
    memo=(
        "장소: 부산 벡스코(BEXCO)\n"
        "BTC(일반 관람): 2026년 11월 19일(목) ~ 22일(일) 4일간\n"
        "BTB(비즈니스): 2026년 11월 19일(목) ~ 21일(토) 3일간 (예상)\n"
        "운영 시간: 오전 10시 ~ 오후 6시\n"
        "주최: 한국게임산업협회(K-GAMES)\n"
        "공동 주관: G-STAR 조직위원회, 부산정보산업진흥원\n"
        "공식 홈페이지: www.gstar.or.kr"
    )
)

# ② 입장권 예매 오픈 (전년도 패턴 기준 10월 중순 예상)
add_entry(
    title="🎟️ 지스타 2026 입장권 예매 오픈 (예상)",
    start="2026-10-15",
    status="예정",
    priority="🔴 높음",
    categories=["개인"],
    memo=(
        "⚠️ 공식 예매 일정 미발표 — 전년도 패턴 기준 예상치\n"
        "예상 오픈: 2026년 10월 중순 (2025년은 10월 14일 오후 3시)\n"
        "예상 판매처: 예스24 (전년도 단독 판매)\n"
        "예상 가격: 성인 15,000~18,000원 / 청소년 8,000원 (미확정)\n"
        "구매 한도: 1인 최대 2매 (예상)\n"
        "⚠️ 100% 온라인 예매만 가능 — 현장 구매 불가\n"
        "→ 공식 홈페이지(gstar.or.kr)에서 정확한 일정 확인 필수"
    )
)

# ③ 예매 취소 마감
add_entry(
    title="⏰ 지스타 2026 입장권 취소·환불 마감",
    start="2026-11-18",
    status="예정",
    priority="🟡 보통",
    categories=["개인"],
    memo=(
        "예매 취소 마감: 관람 당일 하루 전 오후 17:00까지\n"
        "예매 판매 마감: 관람 당일 하루 전 24:00\n"
        "마감 이후 취소·환불 불가\n"
        "예: 11월 19일 관람 → 11월 18일 17:00까지 취소 가능\n"
        "⚠️ 확정 정책은 공식 홈페이지에서 재확인 필수"
    )
)

# ④ 준비물 체크리스트 (2026 업데이트)
add_entry(
    title="🎒 지스타 2026 관람 준비물 체크리스트",
    start="2026-11-19",
    end="2026-11-22",
    status="예정",
    priority="🟡 보통",
    categories=["개인"],
    memo=(
        "[필수]\n"
        "• 신분증: 주민등록증 또는 운전면허증 (미지참 시 입장 불가)\n"
        "• 스마트폰: QR코드 제시 → 현장에서 팔찌로 교환\n"
        "• 보조배터리: SNS 팔로우·이벤트 인증으로 배터리 소모 빠름\n"
        "\n[권장]\n"
        "• 크로스백 또는 소형 백팩 (양손 자유, 귀중품 보관)\n"
        "• 편한 신발 (장시간 이동·대기)\n"
        "• 간식·생수 (전시장 내 혼잡·가격 높음)\n"
        "• 핫팩 1~2개 (11월 부산 야외 대기 쌀쌀함)"
    )
)

# ⑤ 현장 팁 (2026 업데이트)
add_entry(
    title="💡 지스타 2026 관람 현장 팁",
    start="2026-11-19",
    end="2026-11-22",
    status="예정",
    priority="🟢 낮음",
    categories=["개인"],
    memo=(
        "[입장 시간 전략]\n"
        "• 10시 입장: 인기 부스 대기줄 선점 / 굿즈 소진 전 구매 유리\n"
        "• 12시 입장: 초반 혼잡 회피, 여유로운 관람\n"
        "• 목·금요일이 토·일요일보다 혼잡도 낮음 → 평일 방문 추천\n"
        "\n[혼잡 시간대 주의]\n"
        "• 오전 개장 직후 / 오후 2~4시 → 대기줄 최장\n"
        "• 인기 부스는 폐장 직전 타임 노리기\n"
        "\n[관람 규정]\n"
        "• 위험물 반입 금지 (날카로운 소품 등)\n"
        "• 공공 법규 위반 코스튬 착용 시 입장 제한\n"
        "• 일부 부스 별도 사전 예약 필요 (사전 확인)\n"
        "\n[교통]\n"
        "• 지하철 2호선 센텀시티역 하차 → 벡스코 도보 5분\n"
        "• 행사 기간 주차 극혼잡 → 대중교통 강력 권장"
    )
)

# ⑥ 관람 계획 (직접 작성용)
add_entry(
    title="📅 지스타 2026 관람 계획 (직접 작성)",
    start="2026-11-21",
    status="예정",
    priority="🟡 보통",
    categories=["개인"],
    memo=(
        "관람 희망일: 11월 21일(토) — 필요 시 날짜 변경\n"
        "입장 시간대: 10시 / 12시 중 선택 예정\n"
        "목표 부스: (입력 예정)\n"
        "동행 인원: (입력 예정)\n"
        "\n[TO-DO]\n"
        "□ 공식 홈페이지(gstar.or.kr)에서 예매 오픈일 확인\n"
        "□ 예매 오픈일 알림 설정\n"
        "□ 입장권 예매 완료 후 QR 저장\n"
        "□ 당일 신분증 지참 확인\n"
        "□ KTX 등 교통편 사전 예약"
    )
)


# ── 완료 요약 ─────────────────────────────────────────────
print(f"""
{'='*55}
  처리 완료
{'='*55}
  [변경] 2025년 항목 {len(IDS_2025)}개 → 상태 '완료'
  [추가] 2026년 항목 6개:
    • 🎮 BTC 전시       2026-11-19 ~ 11-22
    • 🎟️ 입장권 예매     2026-10-15 (예상)
    • ⏰ 취소·환불 마감  2026-11-18
    • 🎒 준비물 체크리스트
    • 💡 현장 팁
    • 📅 관람 계획 (직접 작성)
""")
