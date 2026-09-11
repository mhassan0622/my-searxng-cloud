import json
import requests
import urllib.parse

KEYWORDS = [
    "nature", "technology", "cars", "cyberpunk", 
    "architecture", "space", "animals", "ocean"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

all_data = {
    "images": [],
    "videos": []
}

print("Starting Robust Web Scraper...")

for kw in KEYWORDS:
    print(f"Fetching data for: {kw}")

    # 1. OPENVERSE GLOBAL WEB SEARCH (Indexed images across the web)
    try:
        ov_url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(kw)}&page_size=20"
        res = requests.get(ov_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            results = res.json().get('results', [])
            for item in results:
                img_url = item.get('url')
                thumb = item.get('thumbnail') or img_url
                if img_url and img_url.startswith('http'):
                    all_data["images"].append({
                        "keyword": kw,
                        "title": (item.get('title') or kw)[:45],
                        "image_url": img_url,
                        "thumbnail": thumb,
                        "engine": f"WEB-{item.get('provider', 'OPEN').upper()}"
                    })
    except Exception as e:
        print(f"Openverse error for {kw}: {e}")

    # 2. WIKIMEDIA COMMONS IMAGES (Fallback & High-res)
    try:
        wiki_img_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(kw)}&gsrnamespace=6&gsrlimit=10&prop=imageinfo&iiprop=url|thumburl&iiurlwidth=400"
        w_res = requests.get(wiki_img_url, headers=HEADERS, timeout=10)
        if w_res.status_code == 200:
            pages = w_res.json().get('query', {}).get('pages', {})
            for pid, info in pages.items():
                imageinfo = info.get('imageinfo', [{}])[0]
                orig_url = imageinfo.get('url')
                thumb_url = imageinfo.get('thumburl')
                if orig_url and not orig_url.endswith(('.svg', '.pdf', '.ogg', '.webm')):
                    all_data["images"].append({
                        "keyword": kw,
                        "title": info.get('title', kw).replace('File:', '')[:45],
                        "image_url": orig_url,
                        "thumbnail": thumb_url or orig_url,
                        "engine": "WIKIMEDIA-WEB"
                    })
    except Exception as e:
        print(f"Wiki image error for {kw}: {e}")

    # 3. WIKIMEDIA COMMONS & ARCHIVE DIRECT VIDEOS
    try:
        wiki_vid_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(kw)}+filetype:video&gsrlimit=8&prop=imageinfo&iiprop=url|thumburl&iiurlwidth=400"
        v_res = requests.get(wiki_vid_url, headers=HEADERS, timeout=10)
        if v_res.status_code == 200:
            pages = v_res.json().get('query', {}).get('pages', {})
            for pid, info in pages.items():
                imageinfo = info.get('imageinfo', [{}])[0]
                vid_url = imageinfo.get('url')
                thumb_url = imageinfo.get('thumburl')
                if vid_url:
                    all_data["videos"].append({
                        "keyword": kw,
                        "title": info.get('title', 'Web Video').replace('File:', '')[:45],
                        "video_url": vid_url,
                        "thumbnail": thumb_url or "https://via.placeholder.com/320x180.png?text=Open+Video",
                        "engine": "OPEN-WEB-VIDEO"
                    })
    except Exception as e:
        print(f"Video error for {kw}: {e}")

# Write results
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print(f"Finished! Gathered {len(all_data['images'])} images and {len(all_data['videos'])} videos.")
