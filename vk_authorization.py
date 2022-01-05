import vk_api, vk_audio
import getpass

import settings


class AuthGenerator:
    @classmethod
    def __init__(self, **kwargs):
        if 'login' and 'password' in kwargs:
            self.login = kwargs['login']
            self.password = kwargs['password']


class AuthCollector:
    @classmethod
    def collect_auth_data(cls):
        cls.login = str(input('Enter VK login: '))
        cls.password = getpass.getpass('Enter VK password: ')
        if len(cls.login) !=0 and len(cls.password) != 0:
            return AuthGenerator(login=cls.login, password=cls.password)
        else:
            print('Invalid VK auth data.\n')
            return AuthCollector.collect_auth_data()


class Authorization:
    @classmethod
    def login(cls):
        try:
            cls.data = AuthCollector.collect_auth_data()
            cls.vk_session = vk_api.VkApi(login=cls.data.login, password=cls.data.password)
            cls.vk_session.auth()
            return vk_audio.VkAudio(vk=cls.vk_session)
        except Exception as exc:
            print(exc)
            return Authorization.login()
