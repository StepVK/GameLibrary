import requests
from Classes.Settings import Settings

# This class will contain methods to login into tapochek.net and find torrents there


class TapochekUser(object):
    URL = 'http://tapochek.net/'
    LOGIN_URL = 'https://tapochek.net/login.php'
    USERNAME = ''
    PASSWORD = ''
    test_url = 'http://tapochek.net/tracker.php?nm=123'
    SETTINGS_FILE_NAME = 'LoginInfo.json'
    current_session = None

    # This reads all settings and is pretty ugly. Make better.
    def __init__(self, *args, **kwargs):
        settings = Settings()
        settings.load_from_folder()
        loginInfo = settings.body[settings.headers.index('LoginInfo')]
        self.USERNAME = loginInfo['Tapochek.net Login']
        self.PASSWORD = loginInfo['Tapochek.net Password']
        super().__init__(*args, **kwargs)

    def construct_search_url(self, keywords, category=None):
        pass

    # Will return cookie for session or None if login failed
    def try_login(self):
        self.current_session = requests.session()
        payload = {'login_username': self.USERNAME,
                   'login_password': self.PASSWORD,
                   'login': '%C2%F5%EE%E4'
                   }
        response = self.current_session.post(self.LOGIN_URL, data=payload)
        return response.ok
