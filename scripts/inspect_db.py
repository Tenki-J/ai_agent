import os
import sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
TOKEN = os.environ.get("NOTION_TOKEN")
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
BASE = "https://api.notion.com/v1"

db = requests.get(f"{BASE}/databases/38663685-d218-81aa-9ec4-eecd8a8e538a", headers=H).json()
print("=== DB 속성 ===")
for k, v in db["properties"].items():
    print(f"  {k}: {v['type']}")

entries = requests.post(f"{BASE}/databases/38663685-d218-81aa-9ec4-eecd8a8e538a/query", headers=H, json={}).json()
print(f"\n=== 총 항목 수: {len(entries['results'])}개 ===")
for e in entries["results"]:
    title = "".join(t["plain_text"] for t in e["properties"]["일정 제목"]["title"])
    sel = e["properties"]["상태"]["select"]
    status = sel.get("name","") if sel else ""
    print(f"  {status:5} | {e['id'][:8]} | {title[:45]}")

blocks = requests.get(f"{BASE}/blocks/38663685-d218-80a5-b9c2-e418b2cb9c60/children", headers=H).json()
print(f"\n=== 캘린더 페이지 블록: {len(blocks['results'])}개 ===")
for b in blocks["results"]:
    btype = b["type"]
    bid = b["id"]
    print(f"  {bid} | {btype}")
