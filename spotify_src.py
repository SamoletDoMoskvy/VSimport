import warnings
import traceback

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from langdetect import detect

from vk_src import VkAudioCollector
from settings import CLIENT_SECRET, CLIENT_ID, CLIENT_REDIRECT_URI


SCOPES = 'user-library-read, user-library-modify, playlist-modify-private'
PLAYLIST_ID: str
IMPORTED_COUNT: int
TOTAL_COUNT: int


class Spotify:
    auth_handler = SpotifyOAuth(scope=SCOPES,
                                client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=CLIENT_REDIRECT_URI
                                )
    client = spotipy.Spotify(auth_manager=auth_handler)
    playlist_id: str

    @classmethod
    def search(cls, track: str, artist=None):
        if artist:
            q = f"track:'{track}'+artist:'{artist}'"
        else:
            q = f"track:'{track}'"
        # TODO: Добавить регулярку для чистки \ в q ('track:\'Wake+Up+Dead\'+artist:\'Megadeth\'')
        return cls.client.search(q=q, type='track', limit=5, locale='RU')

    @classmethod
    def create_playlist(cls):
        cls.playlist_id = cls.client.user_playlist_create(user=cls.client.current_user()['id'],
                                                          name='VK-Music',
                                                          description='Imported music from VK',
                                                          public=False
                                                          )

    @classmethod
    def add_track(cls, track: object):
        return cls.client.user_playlist_add_tracks(user=Spotify.client.current_user()['id'],
                                                   playlist_id=cls.playlist_id,
                                                   tracks=track
                                                   )


class TrackExplorer:
    def __init__(self, track, artist, popularity):
        self.track = track
        self.artist = artist
        self.popularity = popularity

    tracks_group = []

    @classmethod
    def explore(cls, response):
        a = response
        print(response)

    @classmethod
    def sort_by_popularity(cls, tracks_group: list):
        pass
        # cls.track_group = args[0]
        #
        # for i in range(len(cls.track_group) - 1):
        #     for j in range(len(cls.track_group) - i - 1):
        #         if int(cls.track_group[j].popularity) > int(cls.track_group[j + 1].popularity):
        #             cls.track_group[j], cls.track_group[j + 1] = cls.track_group[j + 1], cls.track_group[j]
        #
        # return cls.track_group


class Importer:
    #       record.artist = translit(record.artist, language_code='ru', reversed=True)
    #             for track in cls.response['tracks']['items']:
    #                 TrackExplorer.explore(record, track, cls.response)
    # print(f'Ready!\t {TrackExplorer.len_of_added}/{TrackExplorer.len_of_vk} was imported.')
    vk_tracks = VkAudioCollector.get_audio_records()
    artist = ''
    a = []

    @classmethod
    def start(cls):
        for track in cls.vk_tracks.Audios:
            if len(track.artists_info) == 0:
                pass
            else:
                cls.artist = track.artist.lower()
                if detect(track.artist) == 'ru':
                    artist = None
                else:
                    artist = track.artist.replace(' ', '+')#.lower()
                track = track.title.replace(' ', '+')#.lower()
                response = Spotify.search(track=track, artist=artist)
                TrackExplorer.explore(response)
