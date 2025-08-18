#!/home/womax/.config/rofi/scripts/.env/bin/python
import joblib
from joblib import expires_after
import os
import os.path as path
import shutil
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import sys
import time

# Get client from env variables or default to spotify web player if missing
# Using a custom spotify client should be better to avoir rate limiting
SPOTIFY_CLIENT_ID = os.getenv(
    "SPOTIFY_CLIENT_ID",
    "65b708073fc0480ea92a077233ca87bd")

cache_dir = path.join(
    os.getenv("XDG_CACHE_HOME",
              path.join(os.getenv("HOME"), ".cache")),
    "rofi-spotify")

if path.exists(cache_dir) and not path.isdir(cache_dir):
    shutil.rmtree(cache_dir)

if not path.exists(cache_dir):
    os.makedirs(cache_dir, mode=0o755)

memory = joblib.Memory(cache_dir, verbose=0)

scopes = ["user-top-read", "user-modify-playback-state"]

sp = spotipy.Spotify(
    auth_manager=SpotifyPKCE(
        client_id=SPOTIFY_CLIENT_ID,
        redirect_uri="http://127.0.0.1:9090/login",
        scope=scopes,
        cache_handler=spotipy.CacheFileHandler(
            cache_path=path.join(cache_dir, "credentials"))
    ))

@memory.cache(cache_validation_callback=expires_after(days=30))
def get_top_tracks(limit=200):
    offset = 0
    tracks = []
    while offset < limit:
        reading = min(50, limit-offset)
        tracks += sp.current_user_top_tracks(
            limit=reading,
            offset=offset)["items"]
        offset += reading
    return tracks

def format_track(track):
    track_format = "{title} - {artist}\0info\x1f{track_id}\n"
    return track_format.format(
        title=track["name"],
        artist=track["artists"][0]["name"],
        track_id=track["id"]
    )

def display_default():
    liked_tracks = get_top_tracks()
    for item in liked_tracks:
        print(format_track(item), end="")

def play_track(track_id: str):
    try:
        sp.add_to_queue(f"spotify:track:{track_id}")
    except spotipy.SpotifyException as err:
        print(f"\0message\x1f{err.msg}")
        return
    time.sleep(0.1)
    sp.next_track()

@memory.cache(cache_validation_callback=expires_after(seconds=180))
def search_track(query: str):
    try:
        query_res = sp.search(query, limit=30, type='track')["tracks"]["items"]
        if len(query_res) == 0:
            print("\0message\x1fNo result in search")
            return
        for result in query_res:
            print(format_track(result), end="")
    except spotipy.SpotifyException as err:
        print(f"\0message\x1f{err.msg}")
        return

def main():
    match int(os.getenv("ROFI_RETV", default=-1)):
        case 0:
            # Initial call
            display_default()
        case 1:
            # Selected entry
            play_track(os.getenv("ROFI_INFO", ""))
            exit(0)
        case 2:
            # Custom entry
            track = sys.argv[1]
            search_track(track)
            memory.reduce_size(bytes_limit="10M")
        case _:
            exit(1)

if __name__=="__main__":
    main()
