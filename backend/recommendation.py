import re
import json
import os
import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# ── LOAD .env VARIABLES ────────────────────────────────────────────────────
load_dotenv()

# ── API KEYS ───────────────────────────────────────────────────────────────
TMDB_API_KEY          = os.getenv("TMDB_API_KEY")
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# ── HUGGING FACE INFERENCE API ─────────────────────────────────────────────
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HUGGINGFACE_MODEL     = "google/flan-t5-base"
HUGGINGFACE_API_URL   = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
HF_HEADERS            = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

# ── HELPER: Extract top-n keywords from text ────────────────────────────────
def _extract_keywords(text: str, n: int = 2):
    tokens = re.findall(r"\w+", text.lower())
    filtered = [t for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 3]
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    top = sorted(freq.items(), key=lambda item: item[1], reverse=True)[:n]
    return [k for k,_ in top]

# ── HUGGING FACE FALLBACK ─────────────────────────────────────────────────
def _fallback_hf(movie_name: str):
    prompt = (
        f"You are a helpful assistant. Given the movie '{movie_name}', "
        "suggest 3 book titles and 3 song titles relevant to its theme. "
        "Respond ONLY in this exact JSON format:\n\n"
        "{\n"
        '  "book_recommendations": ["Book 1", "Book 2", "Book 3"],\n'
        '  "music_recommendations": ["Song 1", "Song 2", "Song 3"]\n'
        "}"
    )

    try:
        response = requests.post(
            f"{HUGGINGFACE_API_URL}?wait_for_model=true",
            headers=HF_HEADERS,
            json={"inputs": prompt},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        text = result[0].get('generated_text', '') if isinstance(result, list) else result.get('generated_text', '')

        json_str_match = re.search(r"\{[\s\S]*\}", text)
        if not json_str_match:
            return [], []

        recs = json.loads(json_str_match.group())
        return (
            recs.get('book_recommendations', []),
            recs.get('music_recommendations', [])
        )

    except Exception:
        return [], []

# ── GET MOVIE DETAILS FROM TMDB ─────────────────────────────────────────────
def get_movie_details(movie_name: str):
    try:
        search = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": movie_name},
            timeout=10
        )
        search.raise_for_status()
        results = search.json().get("results", [])
        if not results:
            return None
        movie = results[0]
        overview = movie.get("overview", "")
        genre_ids = movie.get("genre_ids", [])
        primary_genre = genre_ids[0] if genre_ids else None
        return {
            "title": movie.get("title"),
            "overview": overview,
            "primary_genre": primary_genre
        }
    except Exception:
        return None

# ── BOOK RECOMMENDATIONS ───────────────────────────────────────────────────
def get_book_recommendations(overview: str, primary_genre, movie_name: str):
    recs = []
    try:
        # 1) Keyword-based search
        keywords = _extract_keywords(overview, n=2)
        for kw in keywords:
            resp = requests.get(
                "http://openlibrary.org/search.json",
                params={"q": kw, "limit": 3},
                timeout=10
            )
            resp.raise_for_status()
            docs = resp.json().get('docs', [])[:3]
            for d in docs:
                recs.append(f"{d.get('title','')} by {d.get('author_name',['Unknown'])[0]}")

        # 2) Genre-based search if still empty
        if not recs and primary_genre:
            subj = str(primary_genre).replace(' ', '_')
            resp = requests.get(
                f"http://openlibrary.org/subjects/{subj}.json",
                params={"limit": 3},
                timeout=10
            )
            resp.raise_for_status()
            works = resp.json().get('works', [])[:3]
            for w in works:
                recs.append(f"{w.get('title')} by {w.get('authors',[{'name':'Unknown'}])[0]['name']}")

    except Exception:
        pass

    # 3) Raw movie-name search if still empty
    if not recs:
        try:
            resp = requests.get(
                "http://openlibrary.org/search.json",
                params={"q": movie_name, "limit": 3},
                timeout=10
            )
            resp.raise_for_status()
            docs = resp.json().get('docs', [])[:3]
            for d in docs:
                recs.append(f"{d.get('title','')} by {d.get('author_name',['Unknown'])[0]}")
        except Exception:
            pass

    # 4) Hugging Face fallback if still empty
    if not recs:
        books_hf, _ = _fallback_hf(movie_name)
        recs = books_hf

    return recs

# ── MUSIC RECOMMENDATIONS ──────────────────────────────────────────────────
def get_music_recommendations(overview: str, primary_genre, movie_name: str):
    recs = []
    try:
        auth = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth)

        # 1) Keyword-based search
        keywords = _extract_keywords(overview, n=2)
        for kw in keywords:
            results = sp.search(q=kw, type="track", limit=3)
            items = results.get("tracks", {}).get("items", [])
            for t in items:
                recs.append(f"{t['name']} by {t['artists'][0]['name']}")

    except Exception:
        # if Spotify error, we'll fallback below
        pass

    # 2) Raw movie-name search if still empty
    if not recs:
        try:
            auth = SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            )
            sp = spotipy.Spotify(auth_manager=auth)
            results = sp.search(q=movie_name, type="track", limit=3)
            items = results.get("tracks", {}).get("items", [])
            for t in items:
                recs.append(f"{t['name']} by {t['artists'][0]['name']}")
        except Exception:
            pass

    # 3) Hugging Face fallback if still empty
    if not recs:
        _, music_hf = _fallback_hf(movie_name)
        recs = music_hf

    return recs

# ── COMBINED CALL ───────────────────────────────────────────────────────────
def get_recommendations(movie_name: str):
    details = get_movie_details(movie_name)
    if not details:
        # If TMDB lookup fails, do raw-name searches first
        books = get_book_recommendations("", None, movie_name)
        music = get_music_recommendations("", None, movie_name)
        # then HF if still empty
        if not books or not music:
            books_hf, music_hf = _fallback_hf(movie_name)
            books = books or books_hf
            music = music or music_hf
        return {"book_recommendations": books[:3], "music_recommendations": music[:3]}

    overview = details["overview"]
    genre = details["primary_genre"]

    books = get_book_recommendations(overview, genre, movie_name)
    music = get_music_recommendations(overview, genre, movie_name)

    # final HF fallback if needed
    if not books or not music:
        books_hf, music_hf = _fallback_hf(movie_name)
        books = books or books_hf
        music = music or music_hf

    return {"book_recommendations": books[:3], "music_recommendations": music[:3]}
