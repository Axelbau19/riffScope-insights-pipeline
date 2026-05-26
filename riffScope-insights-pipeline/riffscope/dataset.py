from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer
import spotipy
import os
import time
import requests
import pandas as pd


from riffscope.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from spotipy.oauth2 import SpotifyClientCredentials
#connector
spotify= spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))
#genres
genres = {
    "alternative": ["rock","punk","metal","alternative","indie","hard-rock","grunge","garage-rock","shoegaze"],
    "comercial": ["pop","latin-pop","reggaeton","dance","trap","k-pop","hip-hop","corridos-tumbados","regional-mexican"]

}

def save_data_csv(merge):
    for group,tracks in merge.items():
        df = pd.DataFrame(tracks)
        df["group"]=group
        df.to_csv(RAW_DATA_DIR / f"{group}.csv",index=False)
        logger.info(f"{group}:{len(df)} tracks")

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

def merge_tracks(data_tracks,all_track_features):
    merged = {}
    for group, tracks in data_tracks.items():
        features_by_spotify = { feature["href"].split("/")[-1]: feature for feature in all_track_features[group] }
        for track in tracks:
            spotify_id = track["id"]
            if spotify_id in features_by_spotify:
                feature=features_by_spotify[spotify_id]
                merged.setdefault(group, []).append({              
                "id": spotify_id,
                "name": track["name"],
                "artists":", ".join([a["name"] for a in track["artists"]]),
                "release_date": track["album"]["release_date"],
                "acousticness": feature["acousticness"],
                "danceability": feature["danceability"],
                "energy": feature["energy"],
                "valence": feature["valence"],
                })
    return merged

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
            time.sleep(1)
        except Exception as e:
            logger.error(f"{e}")
            break
    return tracks

        

def search_track(genres,limit,pages):
    data_tracks = {}
    for group, genre_list in genres.items():
            group_tracks = []
            for genre in genre_list:
                group_tracks.extend(fetch_track_for_genres(genre,limit,pages))
            data_tracks[group] = list({ t["id"]: t for t in group_tracks }.values())
    return data_tracks






app = typer.Typer()

@app.command()
def main():
    #10-50
    data=search_track(genres=genres,limit=10,pages=20)
    features=get_audio_features(data)
    merge=merge_tracks(data,features)
    save_data_csv(merge)



if __name__ == "__main__":
    app()
