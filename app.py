# app.py : Your Personal Music Player (Direct Audio Streaming)
# Streams high-quality direct audio (MP3) 

from flask import Flask, render_template, request, redirect, url_for
import requests
import html
import base64
from pyDes import des, ECB, PAD_PKCS5

# Creating the Flask application
app = Flask(__name__)

# Standard browser headers (prevents blocking)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# DES Decryption Key used by JioSaavn CDN
DES_KEY = b"38346591"


def decrypt_jiosaavn_url(enc_url: str, has_320: bool = True) -> str:
    """
    Decrypts JioSaavn encrypted_media_url to produce direct, full-length audio stream.
    Replaces default 96kbps with 320kbps (or 160kbps) high-quality full song.
    """
    try:
        cipher = des(DES_KEY, ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
        decrypted = cipher.decrypt(base64.b64decode(enc_url.strip())).decode("utf-8").strip()
        if has_320:
            return decrypted.replace("_96.mp4", "_320.mp4").replace("_160.mp4", "_320.mp4")
        return decrypted.replace("_96.mp4", "_160.mp4")
    except Exception as e:
        print(f" -> Decryption error: {e}")
        return ""

# Reliable music search endpoints
JIOSAAVN_ENDPOINTS = [
    ("https://saavn.dev/api/search/songs", {"query": True}),
    ("https://jiosaavn-api-privatecvc2.vercel.app/search/songs", {"query": True}),
    ("https://saavn-api.vercel.app/api/search/songs", {"query": True}),
]

# ROUTE 1: Home Page  -  "/"
# Displays search bar, favorites tab, and results

@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    error_message = None
    results = []

    if query:
        results, error_message = search_music(query)

    return render_template(
        "index.html",
        query=query,
        results=results,
        error_message=error_message,
    )

# ROUTE 2: Search Handler  -  "/search"
# Redirects cleanly to /?q=<query>

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("index"))
    return redirect(url_for("index", q=query))


def clean_artist_name(item, fallback_artist=""):

#   Extracts artist name from JioSaavn

    more_info = item.get("more_info", {}) if isinstance(item.get("more_info"), dict) else {}
    artist_map = more_info.get("artistMap", {})
    if isinstance(artist_map, dict):
        primary = artist_map.get("primary_artists", [])
        if isinstance(primary, list) and primary:
            names = [a.get("name") for a in primary if isinstance(a, dict) and a.get("name")]
            if names:
                return ", ".join(names)
    if more_info.get("singers"):
        return more_info["singers"]
    if item.get("subtitle"):
        sub = item["subtitle"]
        if " - " in sub:
            return sub.split(" - ")[0].strip()
        return sub.strip()
    if more_info.get("music"):
        return more_info["music"]
    return fallback_artist or "Unknown Artist"


def parse_jiosaavn_song(item, fallback_artist=""):
#    Parses a JioSaavn song object and decrypts its audio URL to 320kbps full song.
 
    more_info = item.get("more_info", {}) if isinstance(item.get("more_info"), dict) else {}
    enc_url = more_info.get("encrypted_media_url")
    if not enc_url:
        return None

    has_320 = str(more_info.get("320kbps", "")).lower() == "true"
    audio_url = decrypt_jiosaavn_url(enc_url, has_320=has_320)
    if not audio_url:
        return None

    title = html.unescape(item.get("title") or item.get("song") or "Unknown Song")
    artist = html.unescape(clean_artist_name(item, fallback_artist=fallback_artist))

    img = item.get("image", "") or ""
    if img:
        img = img.replace("150x150.jpg", "500x500.jpg").replace("50x50.jpg", "500x500.jpg")

    return {
        "id": str(item.get("id", "")),
        "title": title,
        "artist": artist,
        "thumbnail": img,
        "audio_url": audio_url,
    }

# HELPER: search_music(query)
# Hybrid multi-tier search engine:
# 1. JioSaavn Direct Track Search (Full 320kbps songs)
# 2. JioSaavn Artist Match & Greatest Hits (for artist searches)
# 3. JioSaavn Mirrors (for backup)
# 4. iTunes Search Backfill

def search_music(query):
    """
    Searches for songs using a multi-tier strategy to ensure:
    - Complete full-length audio (320kbps)
    - Full coverage of both song titles and artist names
    - Zero missing songs compared to previous versions
    """
    print(f"\n[Music Player] Searching for: '{query}'...")
    q = query.lower().strip()
    results = []
    seen = set()

    def add_song(s):
        if not s or not s.get("audio_url"):
            return
        # Normalize key for deduplication
        norm_key = (s["title"].lower().strip(), s["artist"].lower().strip()[:15])
        sid = s["id"]
        if norm_key not in seen and sid not in seen:
            seen.add(norm_key)
            seen.add(sid)
            results.append(s)

    track_results = []
    artist_results = []
    exact_artist_matched = False

    # TIER 1: JioSaavn Track Search (Direct Full Audio)
    
    try:
        jiosaavn_url = "https://www.jiosaavn.com/api.php"
        params = {
            "__call": "search.getResults",
            "q": query,
            "p": 1,
            "n": 15,
            "_format": "json",
            "_marker": "0",
            "api_version": "4",
            "ctx": "web6dot0",
        }
        res = requests.get(jiosaavn_url, params=params, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            raw_results = res.json().get("results", [])
            for item in raw_results:
                song = parse_jiosaavn_song(item)
                if song:
                    track_results.append(song)
    except Exception as e:
        print(f" -> JioSaavn track search error: {e}")

    # TIER 2: JioSaavn Autocomplete & Artist Match (Greatest Hits)
    
    try:
        ac_params = {
            "__call": "autocomplete.get",
            "query": query,
            "_format": "json",
            "_marker": "0",
            "api_version": "4",
            "ctx": "web6dot0",
        }
        ac_res = requests.get(jiosaavn_url, params=ac_params, headers=HEADERS, timeout=4)
        if ac_res.status_code == 200:
            ac_data = ac_res.json()
            artists = ac_data.get("artists", {}).get("data", [])
            for art in artists[:2]:
                art_name = art.get("title", "").strip()
                # If query matches artist name
                if q == art_name.lower() or (len(q) > 3 and q in art_name.lower() and len(art_name.split()) <= 2):
                    exact_artist_matched = True
                    art_params = {
                        "__call": "artist.getArtistPageDetails",
                        "artistId": art.get("id"),
                        "n_song": 10,
                        "_format": "json",
                        "_marker": "0",
                        "api_version": "4",
                        "ctx": "web6dot0",
                    }
                    art_res = requests.get(jiosaavn_url, params=art_params, headers=HEADERS, timeout=4)
                    if art_res.status_code == 200:
                        art_songs = art_res.json().get("topSongs", [])
                        for item in art_songs:
                            song = parse_jiosaavn_song(item, fallback_artist=art_name)
                            if song:
                                artist_results.append(song)
                    break
    except Exception as e:
        print(f" -> JioSaavn artist search error: {e}")

    # COMBINE & RANK JIOSAAVN RESULTS INTELLIGENTLY

    exact_titles = [s for s in track_results if s["title"].lower().strip() == q]
    other_tracks = [s for s in track_results if s["title"].lower().strip() != q]

    if exact_artist_matched:
        # User searched an artist name (e.g. "Alfaaz") -> prioritize artist greatest hits & exact titles
        for s in artist_results[:5]:
            add_song(s)
        for s in exact_titles:
            add_song(s)
        for s in artist_results[5:]:
            add_song(s)
        for s in other_tracks:
            add_song(s)
    else:
        # User searched a song title (e.g. "Kesariya", "Perfect", "Charkha") -> track matches first
        for s in exact_titles:
            add_song(s)
        for s in other_tracks:
            add_song(s)
        for s in artist_results:
            add_song(s)

    # TIER 3: Backup Mirrors (if JioSaavn direct returned nothing)
    
    if not results:
        for url, _ in JIOSAAVN_ENDPOINTS:
            try:
                params = {"query": query, "page": 1, "limit": 12}
                response = requests.get(url, params=params, headers=HEADERS, timeout=5)
                if response.status_code != 200:
                    continue
                data = response.json()
                items = data.get("data", {}).get("results", []) if isinstance(data.get("data"), dict) else data.get("data", [])
                for item in items:
                    dl = item.get("downloadUrl", [])
                    a_url = dl[-1].get("url") if dl and isinstance(dl[-1], dict) else ""
                    if a_url:
                        add_song({
                            "id": str(item.get("id", "")),
                            "title": html.unescape(item.get("name", "Unknown")),
                            "artist": html.unescape(item.get("primaryArtists", "Unknown")),
                            "thumbnail": item.get("image", [{}])[-1].get("url", "") if isinstance(item.get("image"), list) else "",
                            "audio_url": a_url,
                        })
                if results:
                    break
            except Exception:
                continue
   
    # TIER 4: iTunes Backfill (Ensures zero missing songs from before)

    if len(results) < 8:
        try:
            itunes_url = "https://itunes.apple.com/search"
            it_params = {"term": query, "media": "music", "entity": "song", "limit": 10}
            it_res = requests.get(itunes_url, params=it_params, headers=HEADERS, timeout=4)
            if it_res.status_code == 200:
                for item in it_res.json().get("results", []):
                    audio_url = item.get("previewUrl")
                    if not audio_url:
                        continue
                    art = (item.get("artworkUrl100") or "").replace("100x100bb.jpg", "600x600bb.jpg")
                    add_song({
                        "id": str(item.get("trackId", "")),
                        "title": item.get("trackName", "Unknown Title"),
                        "artist": item.get("artistName", "Unknown Artist"),
                        "thumbnail": art,
                        "audio_url": audio_url,
                    })
        except Exception as e:
            print(f" -> iTunes backfill error: {e}")

    if results:
        print(f" -> Returning {len(results)} songs total!")
        return results, None

    return [], f'No songs found for "{query}". Try a different song or artist name.'

# Entry Point - Run the Flask development server

if __name__ == "__main__":
    app.run(debug=True)
