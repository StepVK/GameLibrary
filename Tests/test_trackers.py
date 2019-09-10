import unittest

from Classes.FreeGOGPCUser import FreeGOGPCUser
from Classes.TPBUser import TPBUser
from Classes.TapochekUser import TapochekUser


class Test_TPBUser(unittest.TestCase):
    def setUp(self):
        self.tpbUser = TPBUser()

    def test_canGetTorrensForWar(self):
        assert(len(self.tpbUser.get_torrents('war')) > 0)


class Test_FreeGOGPCUser(unittest.TestCase):
    def test_canGetTorrentsForWar(self):
        assert(len(FreeGOGPCUser().get_torrents('war')) > 0)


class Test_TapochekUser(unittest.TestCase):
    def SetUp(self):
        self.tap = TapochekUser()

    def test_canGetLoginInfo(self):
        assert(self.tap.USERNAME != '')
        assert(self.tap.PASSWORD != '')

    def test_canAccessSearch(self):
        self.tap.try_login()
