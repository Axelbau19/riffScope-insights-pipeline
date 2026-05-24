from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer
import spotipy
import os


from riffscope.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from spotipy.oauth2 import SpotifyClientCredentials
#connector
spotify= spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))
#genres
genres = {
    "alternative": ["rock","punk","metal","alternative","indie","hard-rock"],
    "comercial": ["pop","latin-pop","reggaeton","dance"]

}

def fetch_track_for_genres(genre,limit,pages):
    tracks = []
    for i in range(pages):
        offset = i*limit
        try:
            result = spotify.search(q=f"genre:{genre}",type="track", limit=limit,offset=offset)
            items = result["tracks"]["items"]
            if not items:
                break
            tracks.extend(items)
        except Exception as e:
            logger.error(f"{e}")
            break
    print(tracks)

        

def search_track(genres,limit,pages):
    for group, genre_list in genres.items():
            for genre in genre_list:
                fetch_track_for_genres(genre,limit,pages)

app = typer.Typer()

@app.command()
def main():
    print(search_track(genres=genres,limit=10,pages=50))



if __name__ == "__main__":
    app()
