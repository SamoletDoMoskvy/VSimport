from os import replace
import warnings
import traceback

import spotipy
import settings

from spotipy.oauth2 import SpotifyOAuth
from vk_music_getter import AudioCollector
from transliterate import translit
from langdetect import detect


class Spotify:
    playlist_exists = False
    playlist_id:str
    scopes = 'user-library-read, user-library-modify, playlist-modify-private'
    client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes,
                                              client_id=settings.SPOTIPY_CLIENT_ID,
                                              client_secret=settings.SPOTIPY_CLIENT_SECRET,
                                              redirect_uri=settings.SPOTIPY_CLIENT_REDIRECT_URI))


    @classmethod
    def search(cls, *args):
        return Spotify.client.search(q=args[0], type='track', limit=5)

    @classmethod
    def create_playlist(cls, *args):
        Spotify.playlist_id = Spotify.client.user_playlist_create(user=Spotify.client.current_user()['id'],
                                                                  name='VK-Music', description='Imported music from VK',
                                                                  public=False)['id']
        Spotify.playlist_exists = True

    @classmethod
    def add_track(cls, *args):
        if not Spotify.playlist_exists:
            Spotify.create_playlist()
        else:
            cls.track_group = args[0]
            try:
                cls.item = [cls.track_group[-1].id]
            except IndexError as ie:
                warnings.warn(f"Error occured while proccessing track\nError is: \n")
                traceback.format_exc()
                print("\n\n")
                return

            #print('Playlist id - ', Spotify.playlist_id)
            #print('Track id - ', cls.item)
            print(f'{cls.track_group[-1].artist} - {cls.track_group[-1].track}')
            return Spotify.client.user_playlist_add_tracks(user=Spotify.client.current_user()['id'],
                                                           playlist_id=Spotify.playlist_id,
                                                           tracks=cls.item)


class TrackData:
    def __init__(self, **kwargs):
        self.track = kwargs['track']
        self.artist = kwargs['artist']
        self.popularity = kwargs['popularity']
        self.id = kwargs['id']


class TrackExplorer:

    group = []
    len_of_vk = 0
    len_of_added = 0

    @classmethod
    def explore(cls, *args):
        cls.checking_track = args[0]
        cls.founded_track = args[1]
        cls.response = args[2]

        cls.checking_track.artist = translit(cls.checking_track.artist, language_code='ru', reversed=True)

        if cls.founded_track['album']['artists'][0]['name'][0:3].lower() in cls.checking_track.artist[0:3].lower():
            if cls.founded_track['name'][0:3].lower() in cls.checking_track.track[0:3].lower():
                TrackCollector.group.append(TrackCollector.add_track(cls.founded_track))

        elif cls.founded_track['name'][0:3].lower() in cls.checking_track.track[0:3].lower():
            TrackCollector.group.append(TrackCollector.add_track(cls.founded_track))

        if cls.founded_track == cls.response['tracks']['items'][-1]:
            Spotify.add_track(TrackExplorer.sort_by_popularity(TrackCollector.group)) # add completer
            TrackExplorer.len_of_added += 1
            TrackCollector.group = []

    @classmethod
    def sort_by_popularity(cls, *args):
        cls.track_group = args[0]

        for i in range(len(cls.track_group)-1):
            for j in range(len(cls.track_group)-i-1):
                if int(cls.track_group[j].popularity) > int(cls.track_group[j+1].popularity):
                    cls.track_group[j], cls.track_group[j+1] = cls.track_group[j+1], cls.track_group[j]

        return cls.track_group


class TrackCollector:
    group = []
    @classmethod
    def add_track(cls, *args):
        cls.track = args[0]
        return TrackData(track=cls.track['name'],
                         artist=cls.track['album']['artists'][0]['name'],
                         popularity=cls.track['popularity'],
                         id=cls.track['id'])


class Searcher:
    # taking tracks after init VK user
    @classmethod
    def search(cls):
        cls.records = AudioCollector.correct_type_transducer()
        TrackExplorer.len_of_vk = len(cls.records)
        for record in cls.records:
            record.track = record.track.replace(' ', '%')
            record.artist = record.artist.replace(' ', '%')
            cls.query = {f'track:{record.track} artist:{record.artist}'}
            cls.response = Spotify.search(cls.query)

            if len(cls.response['tracks']['items']) == 0:
                if detect(record.artist) == 'ru':
                    record.artist = translit(record.artist, language_code='ru', reversed=True)
                    cls.query = {f'track:{record.track}'}
                    cls.response = Spotify.search(cls.query)
                    if len(cls.response['tracks']['items']) == 0:
                        continue
                else:
                    cls.query = {f'track:{record.track}'}
                    cls.response = Spotify.search(cls.query)
                    if len(cls.response['tracks']['items']) == 0:
                        continue

            for track in cls.response['tracks']['items']:
                TrackExplorer.explore(record, track, cls.response)

        print(f'Ready!\t {TrackExplorer.len_of_added}/{TrackExplorer.len_of_vk} was imported.')

Searcher.search()
