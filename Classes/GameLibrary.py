import tkinter
from os import scandir, startfile

from Classes.Game import Game
from Classes.Settings import Settings
from Helpers import (get_installer_paths, launch_installer,
                     remove_extra_spaces_from_string)


# TODO When creating multiple gamelibrary objects (for example subset in search) settings get capiplled multiple times. BAD
class GameLibrary(object):
    def __init__(self):
        self.library = []
        self.settings = Settings()
        self.settings.load_from_folder()
        self.populate()

    # adds a game object to library
    def add_game(self, game):
        self.library.append(game)

    # installs a game by name or returns a list of installers if there are multiple
    def install_game(self, game_name):
        for game in self.library:
            if game.title == game_name:
                # Install that shit.
                if len(game.installers) == 0:
                    temp_text = "There is no recognized installer type for this game. \n"
                    temp_text += "Do you wish to open the game folder to search for in installer manually?"
                    answer = tkinter.messagebox.askquestion(
                        'Whatchagonnado', temp_text)
                    if answer == 'yes':
                        startfile(game.directory)
                    return 0
                elif len(game.installers) == 1:
                    launch_installer(game.installers[0])
                    return 0
                else:
                    return game.installers

    # returns a library as a list of lists
    def as_list(self):
        lst = []
        for i in self.library:
            lst.append(i.as_list())
        return lst

    # populates a library from a directory, ignores '!' dirs and stuff.
    # distrib_source for the whole dir. If several sources, input 0
    def populate_from_dir(self, directory, distrib_source):
        for entry in scandir(directory):
            if (entry.name[0] != "!") and (entry.name != "System Volume Information") and entry.is_dir():
                # titles will include [ and ] for distrib_source, we ignore them for title and parse them for source
                if entry.name.find('[') >= 0:
                    game_title = remove_extra_spaces_from_string(
                        entry.name[0:entry.name.find('[')])
                else:
                    game_title = entry.name
                folder = entry.path
                version = 0.0
                # for installers we use a function
                installer = get_installer_paths(folder)
                if distrib_source != 0:
                    distrib_type = distrib_source
                elif entry.name.find('[') >= 0:
                    distrib_type = remove_extra_spaces_from_string(
                        entry.name[entry.name.find('[')+1:entry.name.find(']')])
                else:
                    distrib_type = "Unknown"
                new_game = Game(game_title, version, folder,
                                installer, distrib_type)
                self.add_game(new_game)

    # populates from all directories in the settings, key = path, value = distrib_source
    def populate(self):
        path_dir = self.settings.dict_by_name('Paths')
        for key in path_dir:
            self.populate_from_dir(key, path_dir[key])

    # finds duplicate games by title. Returns a number of duplicates. Displays message box with results
    def find_duplicates(self):
        number_of_duplicates = 0
        temp = []
        lst_to_populate = []
        for idx, val in enumerate(self.library):
            if val.title not in temp:
                temp.append(val.title)
            else:
                # Duplicate found
                number_of_duplicates += 1
                lst_to_populate.append(val.title)
        # display results
        if number_of_duplicates == 0:
            tkinter.messagebox.showinfo(
                'Results', "No duplicates found in your library!")
        else:
            temp_text = 'Found %d duplicates in your base:\n' % number_of_duplicates
            for i in lst_to_populate:
                temp_text += i + '\n'
            tkinter.messagebox.showinfo('Results', temp_text)
        return number_of_duplicates

    # finds a game/games in library. Returns a subset of game library as a game library
    def find_games_by_name(self, game_name):
        subset = GameLibrary()
        subset.library = []
        game_name = game_name.lower()
        for game in self.library:
            temp = game.title.lower()
            if temp.find(game_name) != -1:
                # seems like a match
                subset.add_game(game)
        return subset
