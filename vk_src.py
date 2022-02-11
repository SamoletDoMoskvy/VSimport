import vk_api
import vk_audio
import getpass


class VkAuthentication:
    def __init__(self):
        self.login: str
        self.password: str
        self.vk_session: object

    def login(self):
        self.login = str(input('Enter VK login: '))
        self.password = str(getpass.getpass('Enter VK password: '))
        self.vk_session = vk_api.VkApi(login=self.login, password=self.password)
        self.vk_session.auth()
        return vk_audio.VkAudio(vk=self.vk_session)


class VkAudioCollector:
    vk_session = VkAuthentication()
    vk_session = vk_session.login()

    @classmethod
    def get_audio_records(cls):
        return cls.vk_session.load(owner_id=None)
