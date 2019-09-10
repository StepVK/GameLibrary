import requests
from Classes.Settings import Settings

# This class will contain methods to login into tapochek.net and find torrents there


class TapochekUser(object):
    URL = 'http://tapochek.net/'
    login_url = 'http://tapochek.net/login.php'
    USERNAME = ''
    PASSWORD = ''
    test_url = 'http://tapochek.net/tracker.php?nm=123#results'
    SETTINGS_FILE_NAME = 'LoginInfo.json'

    # This reads all settings and is pretty ugly. Make better.
    def __init__(self, *args, **kwargs):
        settings = Settings()
        settings.load_from_folder()
        loginInfo = settings.body[settings.headers.index('LoginInfo')]
        self.USERNAME = loginInfo['Tapochek.net Login']
        self.PASSWORD = loginInfo['Tapochek.net Password']
        super().__init__(*args, **kwargs)

    def construct_search_url(self, game_name):
        pass

    def try_test_url(self):
        r = requests.get(self.test_url)
        with open('C:\gay.txt', 'wb') as file:
            file.write(r.text.encode('utf-8', errors='replace'))

    # Will return cookie for session or None if login failed
    def try_login(self):
        with requests.session() as s:
            URL = self.login_url
            USERNAME = self.login
            PASSWORD = self.password
            WTF = '%C2%F5%EE%E4'
            s.get(URL)
            LOGIN_DATA = dict(login_username=USERNAME,
                              login_password=PASSWORD, login=WTF)
            s.post(URL, data=LOGIN_DATA, headers={
                   'Referer': 'http: // tapochek.net / index.php'})
            self.try_test_url()
        return None
