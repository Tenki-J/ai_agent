import requests
from bs4 import BeautifulSoup

BASE = "http://books.toscrape.com"

def get_soup(url):
    r = requests.get(url, timeout=10)
    r.encoding = "utf-8"
    return BeautifulSoup(r.text, "html.parser")

# 1. 메인 페이지에서 카테고리 목록 수집
soup = get_soup(BASE)
category_links = soup.select("div.side_categories ul li ul li a")

results = []

for link in category_links:
    cat_name = link.text.strip()
    cat_url = BASE + "/" + link["href"]

    cat_soup = get_soup(cat_url)

    # 첫 번째 책 카드
    first = cat_soup.select_one("article.product_pod")
    if not first:
        results.append((cat_name, "N/A", "N/A", "N/A"))
        continue

    title = first.select_one("h3 a")["title"]
    price = first.select_one("p.price_color").text.strip()
    star_map = {"One":"1/5","Two":"2/5","Three":"3/5","Four":"4/5","Five":"5/5"}
    star_class = first.select_one("p.star-rating")["class"][1]
    stars = star_map.get(star_class, "?")

    results.append((cat_name, title, price, stars))
    price_clean = price.replace("\xa3", "")
    print(f"[{cat_name}] {title} / {price_clean} / {stars}")

# 결과를 UTF-8 파일로 저장
with open("book_results.txt", "w", encoding="utf-8") as f:
    f.write(f"# 카테고리별 첫 번째 도서 목록 (총 {len(results)}개)\n\n")
    f.write(f"{'#':<4} | {'카테고리':<22} | {'가격(£)':<10} | {'별점':<6} | 제목\n")
    f.write("-" * 110 + "\n")
    for i, (cat, title, price, stars) in enumerate(results, 1):
        price_clean = price.replace("\xa3", "")
        f.write(f"{i:<4} | {cat:<22} | {price_clean:<10} | {stars:<6} | {title}\n")

print(f"\n저장 완료: book_results.txt ({len(results)}개)")
