import json
import requests
import urllib.parse

KEYWORDS = [
    "nature", "technology", "cars", "cyberpunk", 
    "architecture", "space", "animals", "ocean"
]

HEADERS = {
    "User-Agent": "MediaScraperBot/2.0 (https://github.com/mhassan0622; contact@example.com)",
    "Accept": "application/json"
}

all_data = {
    "images": [],
    "videos": []
}

print("Starting Scraper (Images & MP4 Web Videos)...")

for kw in KEYWORDS:
    print(f"Scraping category: {kw}")

    # 1. IMAGES (Openverse & Flickr Global Web Index)
    try:
        ov_url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(kw)}&page_size=20"
        res = requests.get(ov_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            for item in res.json().get('results', []):
                img_url = item.get('url')
                thumb = item.get('thumbnail') or img_url
                if img_url and img_url.startswith('http'):
                    all_data["images"].append({
                        "keyword": kw,
                        "title": (item.get('title') or kw)[:45],
                        "image_url": img_url,
                        "thumbnail": thumb,
                        "engine": f"WEB-{item.get('provider', 'FLICKR').upper()}"
                    })
    except Exception as e:
        print(f"Openverse image error ({kw}): {e}")

    # 2. VIDEOS: INTERNET ARCHIVE (archive.org - Direct Free Web MP4s)
    try:
        ia_url = (
            f"https://archive.org/advancedsearch.php?q={urllib.parse.quote(kw)}+AND+mediatype:movies"
            f"&fl[]=identifier,title&sort[]=downloads+desc&rows=5&page=1&output=json"
        )
        ia_res = requests.get(ia_url, headers=HEADERS, timeout=10)
        if ia_res.status_code == 200:
            docs = ia_res.json().get('response', {}).get('docs', [])
            for doc in docs:
                ident = doc.get('identifier')
                title = doc.get('title') or kw
                if ident:
                    all_data["videos"].append({
                        "keyword": kw,
                        "title": title[:45],
                        "video_url": f"https://archive.org/download/{ident}/{ident}.mp4",
                        "thumbnail": f"https://archive.org/services/img/{ident}",
                        "engine": "INTERNET-ARCHIVE"
                    })
    except Exception as e:
        print(f"Internet Archive video error ({kw}): {e}")

    # 3. VIDEOS: WIKIMEDIA COMMONS (webm/mp4 open media)
    try:
        wiki_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&format=json"
            f"&generator=search&gsrsearch={urllib.parse.quote(kw)}+filetype:bitmap"
            f"&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|mime|thumburl&iiurlwidth=400"
        )
        w_res = requests.get(wiki_url, headers=HEADERS, timeout=10)
        if w_res.status_code == 200:
            pages = w_res.json().get('query', {}).get('pages', {})
            for pid, info in pages.items():
                imginfo = info.get('imageinfo', [{}])[0]
                mime = imginfo.get('mime', '')
                vid_url = imginfo.get('url')
                thumb = imginfo.get('thumburl')
                if ('video' in mime or 'webm' in mime or 'ogg' in mime) and vid_url:
                    all_data["videos"].append({
                        "keyword": kw,
                        "title": info.get('title', 'Web Video').replace('File:', '')[:45],
                        "video_url": vid_url,
                        "thumbnail": thumb or "https://via.placeholder.com/320x180.png?text=Open+Video",
                        "engine": "WIKIMEDIA-OPEN"
                    })
    except Exception as e:
        print(f"Wikimedia video error ({kw}): {e}")

# Save the unified dataset
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print(f"Extraction finished! Images: {len(all_data['images'])}, Videos: {len(all_data['videos'])}")
