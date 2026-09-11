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
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9"
}

@app.route('/')
def home():
    return "All-Internet Web Search Engine Active!"

@app.route('/images', methods=['GET'])
def get_images():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    results = []

    # 1. OPENVERSE GLOBAL WEB (Millions of web images: Flickr, Wikimedia, WordPress blogs, Digital Archives)
    try:
        ov_url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(q)}&page_size=30"
        ov_res = requests.get(ov_url, headers=HEADERS, timeout=6)
        if ov_res.status_code == 200:
            for item in ov_res.json().get('results', []):
                img_url = item.get('url')
                thumb = item.get('thumbnail') or img_url
                provider = item.get('provider', 'WEB').upper()
                if img_url and img_url.startswith('http'):
                    results.append({
                        "title": (item.get('title') or q)[:50],
                        "image_url": img_url,
                        "thumbnail": thumb,
                        "engine": f"WEB-{provider}"
                    })
    except Exception:
        pass

    # 2. WIKIMEDIA GLOBAL WEB COMMONS (Original web photography & high-res)
    try:
        wiki_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&format=json"
            f"&generator=search&gsrsearch={urllib.parse.quote(q)}&gsrnamespace=6&gsrlimit=15"
            f"&prop=imageinfo&iiprop=url|thumburl&iiurlwidth=400"
        )
        w_res = requests.get(wiki_url, headers=HEADERS, timeout=6)
        if w_res.status_code == 200:
            pages = w_res.json().get('query', {}).get('pages', {})
            for pid, info in pages.items():
                imginfo = info.get('imageinfo', [{}])[0]
                orig_url = imginfo.get('url')
                thumb_url = imginfo.get('thumburl')
                if orig_url and not orig_url.endswith(('.svg', '.pdf', '.ogg', '.webm')):
                    results.append({
                        "title": info.get('title', q).replace('File:', '')[:50],
                        "image_url": orig_url,
                        "thumbnail": thumb_url or orig_url,
                        "engine": "WIKIMEDIA-WEB"
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

    # INTERNET ARCHIVE (Real Open Web MP4 Videos)
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
