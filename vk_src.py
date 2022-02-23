import vk_api
import vk_audio
import getpass


class VkAuthentication:
    login: str
    password: str
    vk_session: object

    @classmethod
    def login(cls):
        cls.login = str(input('Enter VK login: '))
        cls.password = str(getpass.getpass('Enter VK password: '))
        cls.vk_session = vk_api.VkApi(login=cls.login, password=cls.password)
        cls.vk_session.auth()
        return vk_audio.VkAudio(vk=cls.vk_session)


class VkAudioCollector:
    vk_session = VkAuthentication.login()

    @classmethod
    def get_audio_records(cls) -> object:
        return cls.vk_session.load(owner_id=None)
