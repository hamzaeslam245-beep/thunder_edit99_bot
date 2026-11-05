import requests, json, os, sys
from bs4 import BeautifulSoup

BASE = "https://egy.voxcinemas.com"
# الفرع: city-centre-alexandria (إسكندرية) أو city-centre-almaza (ألماظة - القاهرة)
CINEMA = os.environ.get("CINEMA", "city-centre-alexandria")
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

SOURCES = {
    # أفلام نزلت على الموقع
    "whatson": (f"{BASE}/movies/whatson", "🎬 فيلم جديد نزل في VOX: {name}\n{link}"),
    # أفلام ليها حجز/مواعيد في الفرع ده
    "booking": (f"{BASE}/showtimes?c={CINEMA}", "🎟️ الحجز اتفتح في {cinema}: {name}\n{link}#showtimes"),
}


def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
        timeout=20,
    )
    r.raise_for_status()


def get_movies(url):
    html = requests.get(url, timeout=20, headers=HEADERS).text
    soup = BeautifulSoup(html, "html.parser")
    movies = {}
    for a in soup.select('a[href*="/movies/"]'):
        href = a["href"].split("#")[0].split("?")[0]
        slug = href.rstrip("/").split("/movies/")[-1]
        if not slug or "/" in slug or slug in ("whatson", "comingsoon"):
            continue
        movies[slug] = slug.replace("-", " ").title()
    return movies


try:
    seen = json.load(open(FILE, encoding="utf-8")) if os.path.exists(FILE) else {}
except Exception:
    seen = {}

for key, (url, template) in SOURCES.items():
    try:
        movies = get_movies(url)
    except requests.RequestException as e:
        print(key, "فشل الاتصال:", e)
        continue

    print(key, "- لقيت", len(movies), "فيلم")
    if not movies:
        print(key, "- مفيش أفلام اتقرأت، يمكن شكل الصفحة اتغير")
        continue

    old = seen.get(key)
    if old is None:
        send(f"✅ البوت اشتغل ({key})، حفظت {len(movies)} فيلم حالياً. هبعتلك لما يظهر جديد.")
    else:
        for slug, name in movies.items():
            if slug not in old:
                send(template.format(name=name, cinema=CINEMA, link=f"{BASE}/movies/{slug}"))

    seen[key] = sorted(set(old or []) | set(movies))

json.dump(seen, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
