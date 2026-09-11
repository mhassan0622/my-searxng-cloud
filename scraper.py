import json
import os
import requests
import urllib.parse

# Jo queries aapko apne canvas ke liye chahiye unki list
KEYWORDS = ["technology", "cyberpunk", "nature", "space", "cars", "minimalist architecture"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SEARX_NODES = [
    "https://priv.au/search",
    "https://search.ononoki.org/search",
    "https://baresearch.org/search"
]

all_data = {
    "images": [],
    "videos": []
}

print("Starting bulk extraction...")

for kw in KEYWORDS:
    print(f"Scraping for keyword: {kw}")
    
    # 1. Images fetch karein SearXNG nodes se
    for node in SEARX_NODES:
        try:
            url = f"{node}?q={urllib.parse.quote(kw)}&categories=images&format=json"
            res = requests.get(url, headers=HEADERS, timeout=6)
            if res.status_code == 200:
                results = res.json().get('results', [])
                for item in results[:15]:
                    img = item.get('img_src') or item.get('url')
                    thumb = item.get('thumbnail_src') or img
                    if img and img.startswith('http') and not img.endswith('.svg'):
                        all_data["images"].append({
                            "keyword": kw,
                            "title": item.get('title', kw)[:40],
                            "image_url": img,
                            "thumbnail": thumb,
                            "engine": item.get('engine', 'WEB').upper()
                        })
                break
        except Exception as e:
            continue

    # 2. Videos fetch karein Pexels API se
    try:
        p_res = requests.get(
            f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&per_page=8",
            headers={"Authorization": "4z0aGlcFftZ1yh1yndUBefpl0E1rqFVSI8menz1nWYPlQo7eYqp3sZbF"},
            timeout=6
        )
        if p_res.status_code == 200:
            for itm in p_res.json().get("videos", []):
                v_files = itm.get("video_files", [])
                stream = next((v.get("link") for v in v_files if v.get("file_type") == "video/mp4"), None)
                if stream:
                    all_data["videos"].append({
                        "keyword": kw,
                        "title": f"{kw.title()} - Clip {itm.get('id')}",
                        "video_url": stream,
                        "thumbnail": itm.get("image"),
                        "engine": "MP4-DIRECT"
                    })
    except Exception:
        pass

# Output ko single JSON file me dump karein
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print(f"Extraction done! Saved {len(all_data['images'])} images and {len(all_data['videos'])} videos.")
