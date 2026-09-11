import json
import requests
import urllib.parse

# Jo categories/topics aapko chahiye unke keywords yahan barha sakte hain
KEYWORDS = [
    "nature landscape", "technology ai", "cars supercar", "cyberpunk city", 
    "architecture modern", "space galaxy", "wildlife animals", "ocean underwater"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Public SearXNG Nodes jo poore internet (Google, Bing, Qwant, DDG) se search karte hain
SEARX_NODES = [
    "https://priv.au/search",
    "https://searx.be/search",
    "https://search.ononoki.org/search",
    "https://baresearch.org/search"
]

all_data = {
    "images": [],
    "videos": []
}

print("Starting Global Web Scraping...")

for kw in KEYWORDS:
    print(f"Scraping Web for: {kw}")
    
    # 1. IMAGES (Google / Bing / Qwant via SearXNG)
    for node in SEARX_NODES:
        try:
            url = f"{node}?q={urllib.parse.quote(kw)}&categories=images&format=json"
            res = requests.get(url, headers=HEADERS, timeout=6)
            if res.status_code == 200:
                results = res.json().get('results', [])
                count = 0
                for item in results:
                    img = item.get('img_src') or item.get('url')
                    thumb = item.get('thumbnail_src') or img
                    engine = item.get('engine', 'WEB').upper()
                    
                    # Sirf real web images filter karein
                    if img and img.startswith('http') and not img.endswith('.svg'):
                        all_data["images"].append({
                            "keyword": kw,
                            "title": item.get('title', kw)[:45],
                            "image_url": img,
                            "thumbnail": thumb,
                            "engine": engine
                        })
                        count += 1
                        if count >= 20: # Har keyword ki 20 images
                            break
                if count > 0:
                    break
        except Exception:
            continue

    # 2. VIDEOS (YouTube / Vimeo / Web Videos via SearXNG)
    for node in SEARX_NODES:
        try:
            url = f"{node}?q={urllib.parse.quote(kw)}&categories=videos&format=json"
            res = requests.get(url, headers=HEADERS, timeout=6)
            if res.status_code == 200:
                results = res.json().get('results', [])
                count = 0
                for item in results:
                    v_url = item.get('url')
                    thumb = item.get('thumbnail') or "https://via.placeholder.com/320x180.png?text=Web+Video"
                    engine = item.get('engine', 'WEB').upper()
                    
                    if v_url and v_url.startswith('http'):
                        all_data["videos"].append({
                            "keyword": kw,
                            "title": item.get('title', kw)[:45],
                            "video_url": v_url,
                            "thumbnail": thumb,
                            "engine": engine
                        })
                        count += 1
                        if count >= 10: # Har keyword ke 10 videos
                            break
                if count > 0:
                    break
        except Exception:
            continue

# Data save karein
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print(f"Scraping complete! Extracted {len(all_data['images'])} images and {len(all_data['videos'])} videos from Web.")
