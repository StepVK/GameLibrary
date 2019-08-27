import unittest
from Classes.TPBUser import TPBUser
from Classes.FreeGOGPCUser import FreeGOGPCUser


class Test_TPBUser(unittest.TestCase):
    def setUp(self):
        self.tpbUser = TPBUser()
        return super().setUp()

    def test_canGetTorrensForWar(self):
        assert(len(self.tpbUser.get_torrents('war')) > 0)


class Test_FreeGOGPCUser(unittest.TestCase):
    def test_canGetTorrentsForWar(self):
        assert(len(FreeGOGPCUser().get_torrents('war')) > 0)
