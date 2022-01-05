from vk_authorization import Authorization


class AudioTransducer:
    def __init__(self, **kwargs):
        if 'artist' in kwargs and 'title' in kwargs:
            self.artist = kwargs['artist']
            self.track = kwargs['title']


class AudioCollector:
    @classmethod
    def get_audio_records(cls):
        vk = Authorization.login()
        return vk.get_only_audios(
            owner_id=None)  # If owner_id == None -> it will be taken records from authorizated in programm user profile

    @classmethod
    def correct_type_transducer(cls):
        cls.records = AudioCollector.get_audio_records()
        cls.reformated_audio_data = []
        for cls.audio in cls.records:
            item = AudioTransducer(artist=cls.audio.artist, title=cls.audio.title)
            cls.reformated_audio_data.append(item)

        return cls.reformated_audio_data
