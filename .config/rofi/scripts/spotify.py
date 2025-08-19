#!/home/womax/.config/rofi/scripts/.env/bin/python
from diskcache import Cache
import os
import os.path as path
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

track_cache = Cache(path.join(cache_dir, "track_cache"),
                    eviction_policy="least-recently-stored",
                    size_limit=int(10e6))

scopes = ["user-top-read", "user-modify-playback-state"]

sp = spotipy.Spotify(
    auth_manager=SpotifyPKCE(
        client_id=SPOTIFY_CLIENT_ID,
        redirect_uri="http://127.0.0.1:9090/login",
        scope=scopes,
        cache_handler=spotipy.CacheFileHandler(
            cache_path=path.join(cache_dir, "credentials"))
    ))

def get_top_tracks(limit=200):
    offset = 0
    tracks = []
    while offset < limit:
        reading = min(50, limit-offset)
        new_tracks = sp.current_user_top_tracks(
            limit=reading,
            offset=offset)["items"]
        if len(new_tracks) == 0:
            return tracks
        tracks += new_tracks
        offset += reading
    return tracks

def simplify_track_info(track):
    result = {}
    result["id"] = track["id"]
    result["fullname"] = f'{track["name"]} - {track["artists"][0]["name"]}'
    return result

def get_cached_tracks():
    if len(track_cache) == 0:
        tt = get_top_tracks(500)
        for track in tt:
            track_cache[track["id"]] = simplify_track_info(track)
    return [track_cache[k] for k in track_cache]

def search_track(query: str):
    search_rs = sp.search(query, limit=10, type='track')["tracks"]["items"]
    return [simplify_track_info(t) for t in search_rs]

def play_track(track_id: str, track_fullname: str, now=True):
    if track_id == "":
        return
    try:
        to_play = {
            "id": track_id,
            "fullname": track_fullname
        }
        sp.add_to_queue(f"spotify:track:{to_play['id']}")
        track_cache[to_play['id']] = to_play
    except spotipy.SpotifyException as err:
        print(f"{err.msg}", file=sys.stderr)
        return
    if now:
        time.sleep(0.1)
        sp.next_track()

def format_track(track):
    track_format = "{fullname}\0info\x1f{track_id}\n"
    return track_format.format(
        fullname=track["fullname"],
        track_id=track["id"]
    )

def display_track_list(track_list=None):
    if track_list is None:
        track_list = get_cached_tracks()
    for item in track_list:
        print(format_track(item), end="")
        
controls = {
    "Next": sp.next_track,
    "Play": sp.start_playback,
    "Pause": sp.pause_playback,
    "Previous": sp.previous_track,
}
        
def display_controls():
    for k, _ in controls.items():
        print(k)
        
def main():
    rofi_retv = int(os.getenv("ROFI_RETV", default=-1));
    print(rofi_retv, file=sys.stderr)
    match rofi_retv:
        case 0:
            # Initial call
            # enable custom hot key
            print("\0use-hot-keys\x1ftrue")
            display_controls()
            display_track_list()
        case 1:
            # Selected entry
            # Default behavior to play the track immediatly
            if sys.argv[1] in controls.keys():
                controls[sys.argv[1]]()
                return
            
            play_track(os.getenv("ROFI_INFO", ""), sys.argv[1])
            
        case 2:
            # Custom entry
            track = sys.argv[1]
            display_track_list(search_track(track))
            
        case 10:
            # Custom hot key 1
            # Add entry to the queue
            if sys.argv[1] in controls.keys():
                return
            
            play_track(os.getenv("ROFI_INFO", ""),
                       sys.argv[1],
                       now=False)
        case _:
            exit(1)

if __name__=="__main__":
    main()
