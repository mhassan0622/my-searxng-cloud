import json
import re
import requests
import urllib.parse

KEYWORDS = [
    "nature landscape", "technology ai", "cars supercar", "cyberpunk city", 
    "architecture modern", "space galaxy", "wildlife animals", "ocean underwater"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

all_data = {
    "images": [],
    "videos": []
}

print("Starting Direct Web Scraping...")

for kw in KEYWORDS:
    print(f"Fetching data for: {kw}")
    
    # 1. DUCKDUCKGO WEB IMAGES
    try:
        token_url = f"https://duckduckgo.com/?q={urllib.parse.quote(kw)}&t=h_&iax=images&ia=images"
        session = requests.Session()
        res = session.get(token_url, headers=HEADERS, timeout=10)
        match = re.search(r'vqd=([\d-]+)&', res.text)
        
        if match:
            vqd = match.group(1)
            img_api = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={urllib.parse.quote(kw)}&vqd={vqd}&f=,,,&p=1"
            img_res = session.get(img_api, headers=HEADERS, timeout=10)
            if img_res.status_code == 200:
                data = img_res.json().get('results', [])
                for itm in data[:20]:
                    img_url = itm.get('image')
                    thumb_url = itm.get('thumbnail')
                    if img_url and img_url.startswith('http'):
                        all_data["images"].append({
                            "keyword": kw,
                            "title": itm.get('title', kw)[:45],
                            "image_url": img_url,
                            "thumbnail": thumb_url or img_url,
                            "engine": "DUCKDUCKGO-WEB"
                        })
    except Exception as e:
        print(f"Image scrape error for {kw}: {e}")

    # 2. WIKIMEDIA COMMONS VIDEOS
    try:
        wiki_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(kw)}+filetype:video&gsrlimit=10&prop=imageinfo&iiprop=url|thumburl"
        wiki_res = requests.get(wiki_url, headers=HEADERS, timeout=10)
        if wiki_res.status_code == 200:
            pages = wiki_res.json().get('query', {}).get('pages', {})
            for page_id, info in pages.items():
                imageinfo = info.get('imageinfo', [{}])[0]
                v_url = imageinfo.get('url')
                thumb = imageinfo.get('thumburl')
                if v_url:
                    all_data["videos"].append({
                        "keyword": kw,
                        "title": info.get('title', 'Web Video').replace('File:', '')[:45],
                        "video_url": v_url,
                        "thumbnail": thumb or "https://via.placeholder.com/320x180.png?text=Open+Video",
                        "engine": "WIKIMEDIA-OPENWEB"
                    })
    except Exception as e:
        print(f"Video scrape error for {kw}: {e}")

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print(f"Scraping complete! Total images: {len(all_data['images'])}, Total videos: {len(all_data['videos'])}")
