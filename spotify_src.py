import spotipy
from spotipy.oauth2 import SpotifyOAuth

from vk_src import VkAudioCollector
from settings import CLIENT_SECRET, CLIENT_ID, CLIENT_REDIRECT_URI
import re


IMPORTED_COUNT = 0
SEARCHING_COUNT = 0
TOTAL_COUNT = 0
SCOPES = 'user-library-read, user-library-modify, playlist-modify-private'


class Spotify:
    auth_manager = SpotifyOAuth(scope=SCOPES,
                                client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=CLIENT_REDIRECT_URI
                                )
    client = spotipy.Spotify(auth_manager=auth_manager)
    playlist_id: str

    @classmethod
    def search(cls, track: str, artist: str = None) -> dict:
        global SEARCHING_COUNT
        SEARCHING_COUNT += 1

        print(f"\n--- SEARCHING: {artist} - {track}---")

        response = cls.client.search(q={f'track:"{track}"+artist:"{artist}"'}, type='track', limit=50
                                     , locale='RU')
        # We remove the artist from the request body, we search only by the name of the song
        if len(response['tracks']['items']) == 0:
            return cls.client.search(q={f'track:"{track}"'}, type='track', limit=10, locale='RU')
        else:
            return response

    @classmethod
    def create_playlist(cls):
        cls.playlist_id = cls.client.user_playlist_create(user=cls.client.current_user()['id'],
                                                          name='VK-Music',
                                                          description='Imported music from VK',
                                                          public=False
                                                          )

    @classmethod
    def add_track(cls, track):
        global IMPORTED_COUNT
        cls.client.playlist_add_items(playlist_id=cls.playlist_id['id'],
                                      items=[track.uri]
                                      )
        IMPORTED_COUNT += 1
        return print(f"--- IMPORTED {track.artist} - {track.track} ---")


class TrackExplorer:
    def __init__(self, track: str, artist: str, popularity: int, uri: str):
        self.track = track
        self.artist = artist
        self.popularity = popularity
        self.uri = uri

    @classmethod
    def explore(cls, response: dict, artist: str) -> list:
        if len(response['tracks']['items']) == 0:
            return None
        else:
            tracks_group = []
            for obj in response['tracks']['items']:

                print(f"FOUNDED: {obj['album']['artists'][0]['name']} - {obj['name']}")

                artist_check = [match.group() for match in re.finditer(obj['artists'][0]['name'].lower(), artist.lower())]

                print(f"ARTIST CHECK: {artist_check} --- {obj['artists'][0]['name'].lower()} | {artist.lower()}")

                # if artist_check:
                tracks_group.append(TrackExplorer(track=obj['name'],
                                                  artist=obj['album']['artists'][0]['name'],
                                                  popularity=obj['popularity'],
                                                  uri=obj['uri']
                                                  )
                                    )
            return tracks_group

    @classmethod
    def sort_by_popularity(cls, tracks_group: list) -> object:
        try:
            return sorted(tracks_group, key=lambda object1: object1.popularity, reverse=True)[0]
        except TypeError or IndexError:
            return None


class Importer:
    vk_tracks = VkAudioCollector.get_audio_records()

    @classmethod
    def start(cls):
        global TOTAL_COUNT
        Spotify.create_playlist()
        for audio in cls.vk_tracks.Audios:
            TOTAL_COUNT += 1
            track = audio.title.replace(' ', '%').replace("'", '').lower()
            artist = audio.artist.replace(' ', '%').replace("'", '').lower()
            response = Spotify.search(track=track, artist=artist)
            tracks_group = TrackExplorer.explore(response=response, artist=audio.artist)
            sorted_track = TrackExplorer.sort_by_popularity(tracks_group) if tracks_group else print("--- CANT IMPORT ---")
            Spotify.add_track(sorted_track) if sorted_track else print("--- CANT IMPORT ---")

        print(f"{IMPORTED_COUNT}/{TOTAL_COUNT}")
