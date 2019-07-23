import requests
# This class will contain methods to login into tapochek.net and find torrents there


class TapochekUser(object):
    url = 'http://tapochek.net/'
    login_url = 'http://tapochek.net/login.php'
    login = 'Roleplayer'
    password = 'Id1JdHa1j0W2oVIrhVdi'
    test_url = 'http://tapochek.net/tracker.php?nm=123#results'

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
