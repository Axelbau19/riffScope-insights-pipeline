import os
import time

import pandas as pd
import requests
import spotipy
import typer
from loguru import logger
from spotipy.oauth2 import SpotifyClientCredentials

from riffscope.config import RAW_DATA_DIR



spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    )
)


GENRES = {
    "alternative": ["rock", "punk", "metal", "alternative", "indie", "hard-rock", "grunge", "garage-rock", "shoegaze"],
    "comercial": ["pop", "latin-pop", "reggaeton", "dance", "trap", "k-pop", "hip-hop", "corridos-tumbados", "regional-mexican"],
}



def _chunks(lst, size=40):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def _fetch_reccobeats_batch(ids: list[str]) -> list[dict]:
    query = "https://api.reccobeats.com/v1/audio-features?ids=" + ",".join(ids)
    while True:
        try:
            response = requests.get(query)
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 5))
                logger.warning(f"Rate limit — esperando {wait}s")
                time.sleep(wait)
                continue
            if response.status_code != 200:
                logger.error(f"ReccoBeats HTTP {response.status_code}: {response.text[:200]}")
                return []
            data = response.json()
            if not data.get("content"):
                logger.warning(f"ReccoBeats sin content: {str(data)[:200]}")
            return data.get("content", [])
        except requests.RequestException as e:
            logger.error(f"Error ReccoBeats: {e}")
            return []



def fetch_tracks_for_genre(genre: str, limit: int, pages: int) -> list[dict]:
    tracks = []
    for page in range(pages):
        try:
            result = spotify.search(q=f"genre:{genre}", type="track", limit=limit, offset=page * limit, market="US")
            items = result["tracks"]["items"]
            if not items:
                break
            tracks.extend(items)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error Spotify [{genre}]: {e}")
            break
    logger.info(f"Género '{genre}': {len(tracks)} tracks")
    return tracks


def search_tracks(genres: dict, limit: int, pages: int) -> dict:
    data = {}
    for group, genre_list in genres.items():
        raw = []
        for genre in genre_list:
            raw.extend(fetch_tracks_for_genre(genre, limit, pages))
        unique = list({t["id"]: t for t in raw}.values())
        data[group] = unique
        logger.info(f"Grupo '{group}': {len(unique)} tracks únicos")
    return data


def get_audio_features(data_tracks: dict) -> dict:
    features_by_group = {}
    for group, tracks in data_tracks.items():
        ids = [t["id"] for t in tracks]
        group_features = []
        for batch in _chunks(ids):
            batch_features = _fetch_reccobeats_batch(batch)
            group_features.extend(batch_features)
            logger.info(f"Grupo '{group}', batch: {len(batch_features)} features")
            time.sleep(2)
        features_by_group[group] = group_features
    return features_by_group


def merge_tracks(data_tracks: dict, features_by_group: dict) -> dict:
    merged = {}
    for group, tracks in data_tracks.items():
        features_index = {
            f["href"].split("/")[-1]: f
            for f in features_by_group.get(group, [])
        }
        for track in tracks:
            feature = features_index.get(track["id"])
            if feature is None:
                continue
            merged.setdefault(group, []).append({
                "id": track["id"],
                "name": track["name"],
                "artists": ", ".join(a["name"] for a in track["artists"]),
                "release_date": track["album"]["release_date"],
                "acousticness": feature["acousticness"],
                "danceability": feature["danceability"],
                "energy": feature["energy"],
                "valence": feature["valence"],
            })
    return merged



def save_data_csv(merged: dict) -> None:
    for group, tracks in merged.items():
        df = pd.DataFrame(tracks)
        df["group"] = group
        path = RAW_DATA_DIR / f"{group}.csv"
        df.to_csv(path, index=False)

        logger.info(f"Guardado {path} — {len(df)} tracks")

app = typer.Typer()

@app.command()
def main():
    tracks = search_tracks(genres=GENRES, limit=10, pages=20)
    features = get_audio_features(tracks)
    merged = merge_tracks(tracks, features)
    save_data_csv(merged)


if __name__ == "__main__":
    app()
