# API KEYS - Ensure you set these as environment variables or replace them with your own keys
# OMDB_API_KEY = os.getenv("OMDB_API_KEY", "1197b38b")
# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyAbRWM_BFSdeBqdYTxIypIwTnNN0ugKSIs")
# YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

from flask import Flask, render_template, request
import requests
import os
app = Flask(__name__)


# API KEYS
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "1197b38b")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyAbRWM_BFSdeBqdYTxIypIwTnNN0ugKSIs")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def get_movie_details(movie_name):
    if not OMDB_API_KEY or OMDB_API_KEY == "YOUR_OMDB_API_KEY":
        return None

    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        poster_url = response.get("Poster", None)
        genre = response.get("Genre", "Unknown Genre")
        title = response.get("Title", "Unknown Title")

        # Try fetching recommendations
        recommendations = get_recommendations_by_genre(genre.split(",")[0])
        if not recommendations:
            recommendations = get_recommendations_by_search(movie_name)

        # Fetch YouTube trailer
        youtube_id = get_youtube_trailer(title) if YOUTUBE_API_KEY and YOUTUBE_API_KEY != "YOUR_YOUTUBE_API_KEY" else None

        return {
            "title": title,
            "poster": poster_url,
            "genre": genre,
            "suggested": recommendations,
            "youtube_id": youtube_id,
        }
    return None


def get_recommendations_by_genre(genre):
    """Fetch movies of the same genre."""
    url = f"http://www.omdbapi.com/?s={genre}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        return [movie["Title"] for movie in response.get("Search", [])[:5]]

    return []


def get_recommendations_by_search(search_text):
    """Fetch related movies if genre-based recommendations fail."""
    url = f"http://www.omdbapi.com/?s={search_text}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        return [movie["Title"] for movie in response.get("Search", [])[:5]]

    return []


def get_youtube_trailer(movie_name):
    """Fetch the YouTube trailer ID."""
    params = {
        "part": "snippet",
        "q": f"{movie_name} official trailer",
        "key": YOUTUBE_API_KEY,
        "type": "video",
        "maxResults": 1
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params).json()
    return response.get("items", [{}])[0].get("id", {}).get("videoId")


@app.route("/", methods=["GET", "POST"])
def index():
    movie_data = None
    if request.method == "POST":
        movie_name = request.form.get("movie")
        movie_data = get_movie_details(movie_name)
    return render_template("index.html", movie=movie_data)


# if __name__ == "_main_":
#     app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
