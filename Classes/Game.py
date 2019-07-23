class Game(object):
    def __init__(self, title, version, directory, installers, distrib_type):
        self.title = title
        self.version = version
        self.directory = directory
        self.installers = installers
        self.distrib_type = distrib_type

# returns a game as a list

    def as_list(self):
        return self.title, self.version, self.distrib_type, self.installers
