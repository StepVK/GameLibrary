from Helpers import fix_nbsp, startfile

# Will use this class to store torrent objects and maybe something more


class Torrent(object):
    def __init__(self, link, name, size, seeds, leeches, site):
        self.link = link
        self.name = name
        self.size = size
        self.seeds = seeds
        self.leeches = leeches
        self.site = site

    def as_list(self):
        return [self.link, self.name, self.size, self.seeds, self.leeches, self.site]

    def as_list_for_tv(self):
        return [self.name, fix_nbsp(self.size), self.seeds, self.site]

    def download_torrent(self):
        startfile(self.link)
