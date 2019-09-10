from Helpers import fix_nbsp, startfile

# Will use this class to store torrent objects and maybe something more


class Torrent(object):
    def __init__(self, link=None, name=None, size=None, seeders=-1, leechers=-1, site=None):
        self.link = link
        self.name = name
        self.size = size
        if not isinstance(seeders, int):
            seeders = int(seeders)
        self.seeders = seeders
        if not isinstance(leechers, int):
            leechers = int(leechers)
        self.leechers = leechers
        self.site = site

    def update_data(self, link=None, name=None, size=None, seeders=None, leechers=None, site=None):
        if link is not None:
            self.link = link
        if name is not None:
            self.name = name
        if size is not None:
            self.size = size
        if seeders is not None:
            if not isinstance(seeders, int):
                seeders = int(seeders)
            self.seeders = seeders
        if leechers is not None:
            if not isinstance(leechers, int):
                leechers = int(leechers)
            self.leechers = leechers
        if site is not None:
            self.site = site

    def as_list(self):
        return [self.link, self.name, self.size, self.seeders, self.leeches, self.site]

    def as_list_for_tv(self):
        return [self.name, fix_nbsp(self.size), self.seeders, self.site]

    def download_torrent(self):
        startfile(self.link)

    def __str__(self):
        return("Torrent: Name = %s, Link = %s(%s), Size = %s, Peers = %d/%d" % (self.name, self.link, self.site, self.size, self.seeders, self.leechers))
