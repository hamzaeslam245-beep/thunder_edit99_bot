import requests, json, os, sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# رابط صفحة سينما فوكس في سيتي سنتر إسكندرية
URL = "https://egy.voxcinemas.com/movies/cinemas/alexandria-city-centre"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"

html = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

movies = {}
# استخراج الأفلام من موقع فوكس (حسب تصميم الموقع للعناوين والروابط)
for a in soup.select('a.movie-card, .movie-item a'):
    name = a.get("title") or a.get_text(strip=True)
    href = a.get("href")
    if name and href:
        movies[href] = name

print(f"لقيت {len(movies)} فيلم")

if not movies:
    print("مفيش أفلام اتقرات")
    sys.exit()

seen = set(json.load(open(FILE))) if os.path.exists(FILE) else set()

if seen:
    for href in movies.keys() - seen:
        movie_name = movies[href]
        movie_url = urljoin(URL, href)
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": f"فيلم جديد نزل في فوكس سيتي سنتر إسكندرية: {movie_name}\n{movie_url}"
            },
        )

json.dump(list(seen.union(movies.keys())), open(FILE, "w"), ensure_ascii=False)
