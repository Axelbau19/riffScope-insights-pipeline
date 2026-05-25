from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer
import spotipy
import os
import time
import requests


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

#Trick
def chunk(lst,size=100):
    for index in range(0,len(lst),size):
        yield lst[index:index+size]


def get_audio_features(data_tracks):
    all_track_features = {}
    for group,tracks in data_tracks.items():
        ids = [track["id"] for track in tracks]
        for batch in chunk(ids):
            ids_query=",".join(batch)
            query = f"https://api.reccobeats.com/v1/audio-features?ids={ids_query}"
            try:
                response=requests.get(query)
                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After",5))
                    logger.warning(f"Rate limite , intentar en {wait}s")
                    time.sleep(wait)
                    continue
                features = response.json().get("content", [])
                all_track_features.setdefault(group, []).extend(features)
            except requests.RequestException as e:
                logger.error(f"Fallo {e}")
                break
    return all_track_features

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
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"{e}")
            break
    return tracks

        

def search_track(genres,limit,pages):
    data_tracks = {}
    for group, genre_list in genres.items():
            group_tracks = []
            for genre in genre_list:
                tracks=fetch_track_for_genres(genre,limit,pages)
                group_tracks.extend(tracks)
            data_tracks[group] = group_tracks
    return data_tracks



app = typer.Typer()

@app.command()
def main():
    #10-50
    data=search_track(genres=genres,limit=1,pages=1)
    features=get_audio_features(data)
    for group, f in features.items():
        logger.info(f"{group}:{f}")



if __name__ == "__main__":
    app()
