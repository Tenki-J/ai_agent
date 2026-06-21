"""
일정 관리 DB에서 2025년 지스타 항목 조회 후 ID 출력
"""
import os
import sys, io, requests, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION, "Content-Type": "application/json"}
DB_ID = "38663685-d218-81aa-9ec4-eecd8a8e538a"

r = requests.post(f"{BASE}/databases/{DB_ID}/query", headers=H, json={"page_size": 100})
pages = r.json().get("results", [])

ids = []
for p in pages:
    pid = p["id"]
    props = p.get("properties", {})
    title = "".join(t.get("plain_text","") for t in props.get("일정 제목",{}).get("title",[]))
    date_obj = props.get("날짜",{}).get("date") or {}
    start = date_obj.get("start","")
    status = props.get("상태",{}).get("select",{})
    status_name = status.get("name","") if status else ""
    ids.append({"id": pid, "title": title, "start": start, "status": status_name})
    print(f"{pid} | {start[:7] if start else 'N/A'} | {status_name} | {title[:40]}")

# 2025년 항목만 필터
target = [x for x in ids if x["start"].startswith("2025")]
print(f"\n--- 2025년 항목 {len(target)}개 ---")
for x in target:
    print(f"  {x['id']} | {x['title'][:40]}")
