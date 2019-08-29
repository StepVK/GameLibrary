import requests
import re

from html.parser import HTMLParser
from Classes.Torrent import Torrent


# This class will hopefully contain methods to login into sites and get magnet links / torrent files from those
class TPBUser(object):
    URL = "https://thepiratebay.icu"
    LINE_REGEX = re.compile(
        r'.*"Details.*">(?<Name>.*)<\/a.*<a href="(?<Link>.*)" title.*Size (?<Size>.*), UL.*<td align="right">(?<Seeders>\d*)<\/td>.*">(?<Leechers>\d*)<.*')

    # 0/99/401 = unknown(relevancy?)/torrents availability?/category(games -> PC)
    def __construct_search_url(self, game_name):
        return "%s/search/%s/0/99/401" % (self.URL, game_name)

    def __remove_useless_HTML(self, result):
        # take unnecessary shit in front and behind of torrents
        return result[result.find('Search results:'):result.find('<div class="ads"')]

    # This will take a result from a http requests and return a list of torrents (objects)
    def __parse_search_result(self, result):
        list_of_torrents = []
        # parse torrents payload
        temp = self.__remove_useless_HTML(result)
        while temp.find('div class="detName"') != -1:
            temp = temp[temp.find('div class="detName"')+19:]
            temp = temp[temp.find('title="Details for ') + 19:]
            tname = temp[:temp.find("\"")]
            temp = temp[temp.find('<a href="magnet') + 9:]
            tlink = temp[:temp.find(
                'title="Download this torrent using magnet"')-2]
            temp = temp[temp.find('class="DetDesc"')+12:]
            temp = temp[temp.find('Size') + 5:]
            tsize = temp[:temp.find(',')]
            temp = temp[temp.find('<td')+3:]
            temp = temp[temp.find('>')+1:]
            tseeds = int(temp[:temp.find('<')])
            temp = temp[temp.find('>') + 5:]
            temp = temp[temp.find('>')+1:]
            tleeches = int(temp[:temp.find('<')])
            tsite = "TPB"
            temp_torrent = Torrent(tlink, tname, tsize,
                                   tseeds, tleeches, tsite)
            # Only add a torrent if there is at least 1 seeder
            if tseeds >= 1:
                list_of_torrents.append(temp_torrent)
        return list_of_torrents

    def __parse_search_result_new(self, result):
        LINE_START = '<div class="detName">'
        LINE_FINISH = '<td class="vertTh">'
        torrentLines = []
        text = self.__remove_useless_HTML(result)
        while text.find(LINE_START) > -1:
            torrentLines.append(
                text[text.find(LINE_START): text.find(LINE_FINISH)])
            text = text[LINE_FINISH + len(LINE_FINISH):]
        return [self.__convert_HTML_into_torrent(line) for line in torrentLines]

    def __convert_HTML_into_torrent(self, line):
        match = re.match(self.LINE_REGEX, line)
        pass

    def get_torrents(self, game_name):
        r = requests.get(self.__construct_search_url(game_name))
        return self.__parse_search_result_new(r.text)
