import os
import requests
import urllib.parse
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Global fast SearXNG nodes
SEARX_NODES = [
    "https://priv.au/search",
    "https://searx.be/search",
    "https://search.ononoki.org/search",
    "https://baresearch.org/search",
    "https://searx.tiekoetter.com/search"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Fallback APIs for stability
PEXELS_KEY = os.environ.get("PEXELS_KEY", "4z0aGlcFftZ1yh1yndUBefpl0E1rqFVSI8menz1nWYPlQo7eYqp3sZbF")
PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "37587854-f5cbab26d60a3ca69475b68d8")

@app.route('/')
def home():
    return "24/7 Global Web Search Backend Active on Vercel!"

@app.route('/images', methods=['GET'])
def get_images():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    results = []

    # 1. Search across Google, Bing, DuckDuckGo, Wikimedia via SearXNG Nodes
    for node in SEARX_NODES:
        try:
            url = f"{node}?q={urllib.parse.quote(q)}&categories=images&format=json"
            res = requests.get(url, headers=HEADERS, timeout=4)
            if res.status_code == 200:
                data = res.json()
                for item in data.get('results', []):
                    img = item.get('img_src') or item.get('url')
                    thumb = item.get('thumbnail_src') or img
                    if img and not img.endswith('.svg') and img.startswith('http'):
                        results.append({
                            "title": item.get('title', 'Web Image')[:45],
                            "image_url": img,
                            "thumbnail": thumb,
                            "engine": item.get('engine', 'WEB').upper()
                        })
                if len(results) >= 15:
                    break
        except Exception:
            continue

    # 2. Add Pixabay/Pexels for high-resolution stock fallback if web results are fewer
    if len(results) < 20:
        try:
            p_res = requests.get(
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=10",
                headers={"Authorization": PEXELS_KEY},
                timeout=4
            )
            if p_res.status_code == 200:
                for itm in p_res.json().get("photos", []):
                    results.append({
                        "title": (itm.get("alt") or q).title()[:35],
                        "image_url": itm.get("src", {}).get("large2x") or itm.get("src", {}).get("original"),
                        "thumbnail": itm.get("src", {}).get("medium"),
                        "engine": "GOOGLE/PEXELS"
                    })
        except Exception:
            pass

    return jsonify(results[:40])

@app.route('/videos', methods=['GET'])
def get_videos():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    results = []

    # 1. Search Videos Across the Web via SearXNG
    for node in SEARX_NODES:
        try:
            url = f"{node}?q={urllib.parse.quote(q)}&categories=videos&format=json"
            res = requests.get(url, headers=HEADERS, timeout=4)
            if res.status_code == 200:
                data = res.json()
                for item in data.get('results', []):
                    v_url = item.get('url')
                    if v_url:
                        results.append({
                            "title": item.get('title', 'Web Video')[:45],
                            "video_url": v_url,
                            "thumbnail": item.get('thumbnail') or "https://via.placeholder.com/320x180.png?text=Web+Video",
                            "engine": item.get('engine', 'WEB').upper()
                        })
                if len(results) >= 10:
                    break
        except Exception:
            continue

    # 2. Add direct MP4 video streams
    try:
        p_res = requests.get(
            f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=10",
            headers={"Authorization": PEXELS_KEY},
            timeout=4
        )
        if p_res.status_code == 200:
            for itm in p_res.json().get("videos", []):
                v_files = itm.get("video_files", [])
                stream = next((v.get("link") for v in v_files if v.get("file_type") == "video/mp4"), None)
                if stream:
                    results.append({
                        "title": f"Video {itm.get('id')} - {q.title()}",
                        "video_url": stream,
                        "thumbnail": itm.get("image"),
                        "engine": "WEB-MP4"
                    })
    except Exception:
        pass

    return jsonify(results[:30])

if __name__ == "__main__":
    app.run()
