import os
import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# API Keys
PEXELS_KEY = os.environ.get("PEXELS_KEY", "4z0aGlcFftZ1yh1yndUBefpl0E1rqFVSI8menz1nWYPlQo7eYqp3sZbF")
PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "37587854-f5cbab26d60a3ca69475b68d8")

@app.after_request
def add_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

def clean_keywords(query):
    words = re.sub(r'[^\w\s]', '', query).split()
    stop_words = {"the", "and", "for", "with", "from", "into", "onto", "that", "this", "ancient", "primitive"}
    meaningful = [w for w in words if w.lower() not in stop_words]
    if len(meaningful) >= 2:
        return " ".join(meaningful[:3])
    elif len(words) >= 2:
        return " ".join(words[:2])
    return query[:30]

@app.route('/')
def home():
    return "24/7 Media Backend is Running!"

@app.route('/images', methods=['GET'])
def get_images():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    search_term = clean_keywords(q)
    results = []

    # 1. Pexels HD Photos
    try:
        p_res = requests.get(
            f"https://api.pexels.com/v1/search?query={requests.utils.quote(search_term)}&per_page=15",
            headers={"Authorization": PEXELS_KEY},
            timeout=7
        )
        if p_res.status_code == 200:
            for itm in p_res.json().get("photos", []):
                results.append({
                    "title": (itm.get("alt") or search_term).title()[:35],
                    "image_url": itm.get("src", {}).get("large2x") or itm.get("src", {}).get("original"),
                    "thumbnail": itm.get("src", {}).get("medium"),
                    "engine": "PEXELS"
                })
    except Exception as e:
        print("Pexels err:", e)

    # 2. Pixabay Photos
    try:
        pix_res = requests.get(
            f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={requests.utils.quote(search_term)}&image_type=photo&per_page=15&safesearch=true",
            timeout=7
        )
        if pix_res.status_code == 200:
            for itm in pix_res.json().get("hits", []):
                results.append({
                    "title": itm.get("tags", "Photo").title()[:35],
                    "image_url": itm.get("largeImageURL"),
                    "thumbnail": itm.get("webformatURL"),
                    "engine": "PIXABAY"
                })
    except Exception as e:
        print("Pixabay err:", e)

    return jsonify(results)

@app.route('/videos', methods=['GET'])
def get_videos():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    search_term = clean_keywords(q)
    results = []

    # 1. Pexels MP4 Direct Streams
    try:
        p_res = requests.get(
            f"https://api.pexels.com/videos/search?query={requests.utils.quote(search_term)}&per_page=12",
            headers={"Authorization": PEXELS_KEY},
            timeout=7
        )
        if p_res.status_code == 200:
            for itm in p_res.json().get("videos", []):
                v_files = itm.get("video_files", [])
                stream = next((v.get("link") for v in v_files if v.get("file_type") == "video/mp4" and (v.get("width", 0) <= 1920)), None)
                if not stream and v_files:
                    stream = v_files[0].get("link")

                if stream:
                    results.append({
                        "title": f"Clip {itm.get('id')} - {search_term.title()}",
                        "video_url": stream,
                        "thumbnail": itm.get("image"),
                        "engine": "PEXELS-MP4"
                    })
    except Exception as e:
        print("Pexels video err:", e)

    # 2. Pixabay MP4 Direct Streams
    try:
        pix_res = requests.get(
            f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={requests.utils.quote(search_term)}&per_page=10&safesearch=true",
            timeout=7
        )
        if pix_res.status_code == 200:
            for itm in pix_res.json().get("hits", []):
                vids = itm.get("videos", {})
                stream = vids.get("medium", {}).get("url") or vids.get("small", {}).get("url")
                thumb = vids.get("medium", {}).get("thumbnail") or f"https://i.vimeocdn.com/video/{itm.get('picture_id')}_640x360.jpg"
                if stream:
                    results.append({
                        "title": itm.get("tags", "Video").title()[:35],
                        "video_url": stream,
                        "thumbnail": thumb,
                        "engine": "PIXABAY-MP4"
                    })
    except Exception as e:
        print("Pixabay video err:", e)

    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
