import json
import re
import urllib.parse
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

@app.route('/')
def home():
    return "24/7 Pure Open Web Engine Active"

@app.route('/images', methods=['GET'])
def get_images():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    results = []

    # 1. QWANT / DUCKDUCKGO WEB IMAGES
    try:
        qwant_url = f"https://api.qwant.com/v3/search/images?q={urllib.parse.quote(q)}&count=25&locale=en_US&offset=0"
        res = requests.get(qwant_url, headers=HEADERS, timeout=6)
        if res.status_code == 200:
            data = res.json().get('data', {}).get('result', {}).get('data', [])
            for item in data:
                img_url = item.get('media')
                thumb = item.get('thumbnail') or img_url
                title = item.get('title') or q
                if img_url and img_url.startswith('http'):
                    results.append({
                        "title": title[:50],
                        "image_url": img_url,
                        "thumbnail": thumb,
                        "engine": "QWANT-WEB"
                    })
    except Exception:
        pass

    # 2. OPENVERSE (Global Web Index: Flickr, Wikimedia, Blogs, Public Archives)
    try:
        ov_url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(q)}&page_size=25"
        res = requests.get(ov_url, headers=HEADERS, timeout=6)
        if res.status_code == 200:
            for item in res.json().get('results', []):
                img_url = item.get('url')
                thumb = item.get('thumbnail') or img_url
                if img_url and img_url.startswith('http'):
                    results.append({
                        "title": (item.get('title') or q)[:50],
                        "image_url": img_url,
                        "thumbnail": thumb,
                        "engine": f"WEB-{item.get('provider', 'INDEX').upper()}"
                    })
    except Exception:
        pass

    # Verification ke liye response return karein
    return jsonify(results[:40])

@app.route('/videos', methods=['GET'])
def get_videos():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    results = []

    # INTERNET ARCHIVE (Real Web Direct MP4s)
    try:
        ia_url = (
            f"https://archive.org/advancedsearch.php?q={urllib.parse.quote(q)}+AND+mediatype:movies"
            f"&fl[]=identifier,title&sort[]=downloads+desc&rows=15&page=1&output=json"
        )
        ia_res = requests.get(ia_url, headers=HEADERS, timeout=6)
        if ia_res.status_code == 200:
            docs = ia_res.json().get('response', {}).get('docs', [])
            for doc in docs:
                ident = doc.get('identifier')
                title = doc.get('title') or q
                if ident:
                    results.append({
                        "title": title[:50],
                        "video_url": f"https://archive.org/download/{ident}/{ident}.mp4",
                        "thumbnail": f"https://archive.org/services/img/{ident}",
                        "engine": "INTERNET-ARCHIVE"
                    })
    except Exception:
        pass

    return jsonify(results[:25])
