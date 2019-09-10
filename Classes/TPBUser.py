import requests
import re

from html.parser import HTMLParser
from Classes.Torrent import Torrent


# This class will hopefully contain methods to login into sites and get magnet links / torrent files from those
class TPBUser(object):
    URL = "https://thepiratebay.icu"
    LINE_START = '<div class="detName">'
    LINE_FINISH = '<td class="vertTh">'
    PAYLOAD_FINISH = '</tbody></table>'

    # 0/99/401 = unknown(relevancy?)/torrents availability?/category(games -> PC)
    def __construct_search_url(self, game_name):
        return "%s/search/%s/0/99/401" % (self.URL, game_name)

    def __remove_useless_HTML(self, result):
        # take unnecessary shit in front and behind of torrents
        text = ''.join([line.strip() for line in result.split('\n')])
        text = text[text.find(
            'Search results:'): text.find('<div class="ads"')]
        text = text[text.find(self.LINE_START):]
        text = text[:text.find(self.PAYLOAD_FINISH)]
        return text

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

    # TODO Make this actually work better than old one and use it
    def __parse_search_result_new(self, result):
        torrentLines = []
        text = self.__remove_useless_HTML(result)
        while text.find(self.LINE_START) > -1:
            torrentLines.append(
                text[text.find(self.LINE_START): text.find(self.LINE_FINISH)])
            text = text[text.find(self.LINE_FINISH) + len(self.LINE_FINISH):]
        return [self.__convert_HTML_into_torrent(line) for line in torrentLines]

    def __convert_HTML_into_torrent(self, line):
        match = re.match(
            r'.*"Details for .*">(?P<Name>.*)<\/a.*href="(?P<Link>magnet:.*)" title="Down.*Size (?P<Size>.*), UL.*<td align="right">(?P<Seeders>\d*)<\/td>.*">(?P<Leechers>\d*)<.*', line)
        if match is None:
            raise (ValueError('Line cannot be parsed to get a torrent: %s' % line))
        tempDict = match.groupdict()
        return Torrent(link=tempDict['Link'], name=tempDict['Name'], size=tempDict['Size'], seeds=tempDict['Seeders'], leechers=tempDict['Leechers'])

    def get_torrents(self, game_name):
        r = requests.get(self.__construct_search_url(game_name))
        if not r.ok:
            raise (Exception('HTTP Request failed with code %d' % r.status_code))
        else:
            return self.__parse_search_result(r.text)

    # remove this later
    def get_torrents_from_string(self, string):
        return self.__parse_search_result_new(string)
