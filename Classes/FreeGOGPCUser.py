import requests

from Classes.Torrent import Torrent

# This class will hopefully work with freegogpcgames.com


class FreeGOGPCUser(object):
    BASE_URL = 'http://freegogpcgames.com'

    # construct the search url
    def __construct_search_url(self, game_name):
        return "%s/?s=%s" % (self.BASE_URL, game_name)

    # TODO Make this look not awful
    def __parse_search_result(self, result):
        temp = result
        torrents = []
        temp = temp[temp.find('<h1 class'):]
        temp = temp[:temp.find("class='page-numbers current'>")]
        # Parse payload. Not torrents yet.
        while temp.find('href="') >= 0:
            temp = temp[temp.find('href="') + 6:]
            temp = temp[temp.find('href="') + 6:]
            tlink = temp[:temp.find('"')]
            temp = temp[temp.find('title="') + 7:]
            tname = temp[:temp.find('"')]
            temp = temp[temp.find('href="') + 6:]
            temp = temp[temp.find('href="') + 6:]
            temp = temp[temp.find('href="') + 6:]
            # We have name and a link with more description. Let's get magnet link + size from there
            r = requests.get(tlink)
            temp2 = r.text
            temp2 = temp2[temp2.find('<em>Size: ') + 10:]
            tsize = temp2[:temp2.find('<')]
            temp2 = temp2[temp2.find('href="magnet:') + 6:]
            tlink2 = temp2[:temp2.find('">')]
            torrents.append(Torrent(link=tlink2, name=tname,
                                    size=tsize, site='FreeGOGPCGames'))
        return torrents

    def get_torrents(self, game_name):
        r = requests.get(self.__construct_search_url(game_name))
        return self.__parse_search_result(r.text)
