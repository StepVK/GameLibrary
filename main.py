from os import scandir
from os import getcwd
from os import path
from os import startfile
from os.path import splitext
from tkinter import *
import tkinter.messagebox
from tkinter.ttk import Treeview
from tkinter.ttk import Scrollbar
import json
import requests


# Global variables
list_of_valid_installer_types = [".exe", '.iso']
global_version = 0.1


# removes extra spaces at the beginning and end of a string
def remove_extra_spaces_from_string(string):
    if string[0] == ' ':
        return remove_extra_spaces_from_string(string[1:])
    elif string[len(string) - 1] == ' ':
        return remove_extra_spaces_from_string(string[:len(string) - 1])
    else:
        return string


def fix_nbsp(string):
    return string[:string.find('&nbsp;')] + ' ' + string[string.find('&nbsp;')+6:]


# Tries to get an installer name inside of a folder may return a list (for multiple installers), or a string
# for 0 or 1 installers found
def get_installer_paths(installer_path):
    lst_of_installers = []
    for entry in scandir(installer_path):
        if entry.is_file():
            filename, extension = splitext(entry.name)
            if extension in list_of_valid_installer_types:
                lst_of_installers.append(entry.path)
        elif entry.is_dir():
            lst_of_installers += get_installer_paths(entry.path)
    return lst_of_installers


# Tries to launch an installer from string. Understands EXE only. Returns zero if the file ext is not good
def launch_installer(string):
    name, ext = splitext(string)
    if ext == ".exe":
        startfile(string)
    elif ext == ".iso":
        startfile(string)
        info = 'The installer, that you have selected is an image file. \n'
        info += 'An attempt to mount it has been made, but you may have to do additional steps to install the game:\n'
        info += 'Check if you have an image mounting tool, check if autoruns are enabled.\n'
        tkinter.messagebox.showinfo('Warning', info)
    else:
        return 0


# Fills the Treeview object (tv) with values from list. If it is a list of lists it will take first n(1+) values in each
# sub-list.
def fill_tv_from_list(tv, lst, n):
    tv.delete(*tv.get_children())
#    if n is not int:
#        return -1
    if n <= 0:
        return -1
    elif n == 1:
        # values are empty, only fill text
        for item in sorted(lst):
            tv.insert('', 'end', text=item[0])
    else:
        # values are not empty
        for item in sorted(lst):
            temp_values = []
            for i in range(1, n):
                temp_values.append(item[i])
            tv.insert('', 'end', text=item[0], values=temp_values)


# Class for the whole app
class MainApp(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(side=TOP, fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # This is for storing different frames of the app

        self.frames = {}
        for F in (MainPage, MultipleInstallPage, SettingsPage, TorrentsPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky=NSEW)

        # Show main page on init

        self.show_frame(MainPage)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()

    # Returns an instance of a page, given it's class name as a string
    def get_page(self, page_class):
        for page in self.frames.values():
            if str(page.__class__.__name__) == page_class:
                return page
        return None


# Class representing the main frame/page of the app
class MainPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        for count in range(0, 10):
            Grid.rowconfigure(self, count, weight=1)
            Grid.columnconfigure(self, count, weight=1)
        # load size from settings and set min max size for window
        controller.maxsize(height=1400, width=1800)
        controller.minsize(height=400, width=600)
        controller.geometry("%dx%d" % (
            my_lib.settings.dict_by_name('Video')['Width'], my_lib.settings.dict_by_name('Video')['Height']))
        controller.title("Game Library %f" % global_version)
        # Treeview for library

        tv = Treeview(self)
        self.library_treeview = tv
        tv.grid(row=0, column=0, rowspan=10, columnspan=10, sticky=(N, E, W, S))
        tv['columns'] = ('Version', 'Source')
        tv.heading('#0', text="Name")
        tv.heading('Version', text="Version")
        tv.heading('Source', text="Source")

        tv.column("#0", anchor='w', minwidth=200)
        tv.column('Version', width=150, minwidth=100, anchor='center')
        tv.column('Source', width=150, minwidth=100, anchor='center')

        # adding scrollbar

        ysb = Scrollbar(self, orient='vertical', command=tv.yview)
        tv.configure(yscroll=ysb.set)
        ysb.grid(row=0, column=9, rowspan=10, sticky='nse')

        # Buttons for the rest

        settings_button = Button(self, text="Settings", command=lambda: controller.show_frame(SettingsPage))
        settings_button.grid(row=10, column=0, sticky=N + S + E + W)

        populate_button = Button(self, text="Load library",
                                 command=lambda: fill_tv_from_list(tv, my_lib.as_list(), 3))
        populate_button.grid(row=10, column=1, sticky=N + S + E + W)

        install_button = Button(self, text="Install game",
                                command=lambda: self.installer_page_button(
                                    my_lib.install_game(tv.item(tv.focus())['text'])))
        install_button.grid(row=10, column=2, sticky=N + S + E + W)

        duplicates_button = Button(self, text="Find duplicates", command=my_lib.find_duplicates)
        duplicates_button.grid(row=10, column=3, sticky=N + S + E + W)

        search_entry = Entry(self, text="")
        search_entry.grid(row=10, column=4, columnspan=3, sticky=N + S + E + W)
        self.torrent_search_entry = search_entry

        search_button = Button(self, text="Find in library", command=lambda: fill_tv_from_list(
            tv, my_lib.find_games_by_name(search_entry.get()).as_list(), 3))
        search_button.grid(row=10, column=7, sticky=N + S + E + W)

        # TODO Make this to look on more different torrents

        torrent_button = Button(self, text="Find on torrents", command=self.torrent_button_on_click)
        torrent_button.grid(row=10, column=8, sticky=N + S + E + W)

        quit_button = Button(self, text="Quit", command=controller.destroy)
        quit_button.grid(row=10, column=9, sticky=N + S + E + W)

    # It will clear the torrent page treeview, upload a new torrent list into current tor list on page, then call the
    # fill_treeview function to display shit and make the page visible
    def torrent_button_on_click(self):
        torrent_list = my_tpb.get_torrents(self.torrent_search_entry.get())
        torrent_list += my_FreeGOG.get_torrents(self.torrent_search_entry.get())
        if len(torrent_list) == 0:
            # There are no torrents
            tkinter.messagebox.showinfo('No luck', "Sorry, no torrents have been found =(")
        else:
            # Some were found, let's proceed
            self.controller.show_frame(TorrentsPage)
            t_page = self.controller.get_page('TorrentsPage')
            t_page.torrents_treeview.delete(*t_page.torrents_treeview.get_children())
            t_page.current_torrents_list = torrent_list
            temp_list = []
            for i in torrent_list:
                temp_list.append(i.as_list_for_tv())
            fill_tv_from_list(t_page.torrents_treeview, temp_list, 4)

    # only do stuff, when something is selected.
    def installer_page_button(self, list_to_choose_from):
        if self.library_treeview.focus() != '':
            if list_to_choose_from == 0:
                # game already being installed, ignore this function
                return 0
            else:
                # seems like there is multiple options, let's proceed
                # filling choices, can't use my fill_tv func, because it's not a list of lists and rather a list of str
                self.controller.show_frame(MultipleInstallPage)
                self.controller.get_page('MultipleInstallPage').temp_tv.delete(
                    *self.controller.get_page('MultipleInstallPage').temp_tv.get_children())
                for item in list_to_choose_from:
                    self.controller.get_page('MultipleInstallPage').temp_tv.insert('', 'end', text=item)
        else:
            # nothing was selected
            return -1


# Class representing the install window
class MultipleInstallPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        # will do a 4x4 grid here
        for count in range(0, 4):
            Grid.rowconfigure(self, count, weight=1)
            Grid.columnconfigure(self, count, weight=1)
        self.temp_tv = Treeview(self)
        temp_tv = self.temp_tv
        temp_tv.grid(row=0, column=0, rowspan=3, columnspan=4, sticky=(N, E, W, S))
        temp_tv.heading('#0', text="Choose one:")
        temp_tv.column("#0", minwidth=300)
    
        # adding scrollbar
    
        ysb = Scrollbar(self, orient='vertical', command=temp_tv.yview)
        temp_tv.configure(yscroll=ysb.set)
        ysb.grid(row=0, column=3, rowspan=3, sticky='nse')
    
        # Buttons for the rest
    
        ok_button = Button(self, text="Ok", command=self.ok_button_click)
        ok_button.grid(row=3, column=0, sticky=N + S + E + W)
    
        cancel_button = Button(self, text="Cancel", command=lambda: controller.show_frame(MainPage))
        cancel_button.grid(row=3, column=3, sticky=N + S + E + W)

    def ok_button_click(self):
        # Should only do stuff is something is selected
        if self.temp_tv.focus() != '':
            installer_path = self.temp_tv.item(self.temp_tv.focus())['text']
            launch_installer(installer_path)
            self.controller.show_frame(MainPage)
        else:
            return -1

        # filling choices, can't use my fill_tv func, because it's not a list of lists and rather a list of str


# Class representing the settings window
class SettingsPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        for count in range(0, 10):
            Grid.rowconfigure(self, count, weight=1)
            Grid.columnconfigure(self, count, weight=1)

        # Paths subsection of settings page treeview + scrollbar + label + two buttons

        tv = Treeview(self)
        self.paths_tree_view = tv
        tv.grid(row=1, column=0, rowspan=3, columnspan=10, sticky=(N, E, W, S))
        tv['columns'] = 'Source'
        tv.heading('#0', text="Path")
        tv.heading('Source', text="Source")
        tv.column("#0", anchor='w', minwidth=200)
        tv.column('Source', width=100, minwidth=50)

        paths_label = Label(self, text="PATHS OF YOUR GAME LIBRARY", font=('Fixedsys', 16))
        paths_label.grid(row=0, column=0, columnspan=10, sticky=N + S + E + W)

        add_button = Button(self, text="Add", command=None)
        add_button.grid(row=4, column=8, sticky=N + S + E + W)

        remove_button = Button(self, text="Remove", command=None)
        remove_button.grid(row=4, column=9, sticky=N + S + E + W)

        ysb = Scrollbar(self, orient='vertical', command=tv.yview)
        tv.configure(yscroll=ysb.set)
        ysb.grid(row=1, column=9, rowspan=3, sticky='nse')

        # Video subsection

        video_label = Label(self, text='Video settings', font=('Courier', 14))
        video_label.grid(row=4, column=0, columnspan=2, sticky=N + S + E + W)

        video_label_w = Label(self, text='Width', font=('Courier', 11))
        video_label_w.grid(row=6, column=0, sticky=N + S + E + W)

        video_label_h = Label(self, text='Height', font=('Courier', 11))
        video_label_h.grid(row=7, column=0, sticky=N + S + E + W)

        width_entry = Entry(self, text='Default width', font=('Courier', 11))
        width_entry.grid(row=6, column=2, sticky=N + S + E + W)

        height_entry = Entry(self, text='Default height', font=('Courier', 11))
        height_entry.grid(row=7, column=2, sticky=N + S + E + W)
        # Buttons for the rest

        save_button = Button(self, text="Save", command=None)
        save_button.grid(row=10, column=8, sticky=N + S + E + W)

        cancel_button = Button(self, text="Cancel", command=lambda: controller.show_frame(MainPage))
        cancel_button.grid(row=10, column=9, sticky=N + S + E + W)


# Class representing the torrent choice window
class TorrentsPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        # setting class variables
        self.current_torrents_list = []
        # will do a 4x4 grid here
        for count in range(0, 4):
            Grid.rowconfigure(self, count, weight=1)
            Grid.columnconfigure(self, count, weight=1)
        self.torrents_treeview = Treeview(self)
        torrents_treeview = self.torrents_treeview
        torrents_treeview.grid(row=0, column=0, rowspan=3, columnspan=4, sticky=(N, E, W, S))
        torrents_treeview.heading('#0', text="Torrent name")
        torrents_treeview.column("#0", minwidth=400)
        torrents_treeview['columns'] = ('size', 'seeders', 'site')
        torrents_treeview.heading('size', text="Torrent size")
        torrents_treeview.heading('seeders', text="Seeders")
        torrents_treeview.heading('site', text="Site")
        torrents_treeview.column('size', width=70, stretch=NO)
        torrents_treeview.column('seeders', width=70, stretch=NO)
        torrents_treeview.column('site', width=100, stretch=NO)

        # adding scrollbar

        ysb = Scrollbar(self, orient='vertical', command=torrents_treeview.yview)
        torrents_treeview.configure(yscroll=ysb.set)
        ysb.grid(row=0, column=3, rowspan=3, sticky='nse')

        # Buttons for the rest

        steal_button = Button(self, text="Steal that shit!", command=self.steal_button_click)
        steal_button.grid(row=3, column=0, sticky=N + S + E + W)

        cancel_button = Button(self, text="Cancel", command=lambda: controller.show_frame(MainPage))
        cancel_button.grid(row=3, column=3, sticky=N + S + E + W)

    # Will identify the torrent by it's name and site (hopefully enough?), find it in the current torrents which was
    # populated by the main page button and invoke the .download in the torrent class. Then will just show the main page
    def steal_button_click(self):
        # probably only should do stuff when something is selected
        if self.torrents_treeview.focus() != '':
            torrent_name = self.torrents_treeview.item(self.torrents_treeview.focus())['text']
            torrent_from = self.torrents_treeview.item(self.torrents_treeview.focus())['values'][2]
            for torrent in self.current_torrents_list:
                if torrent.name == torrent_name and torrent.site == torrent_from:
                    torrent.download_torrent()
                    break
            else:
                # Weird, seems like the torrent couldn't be found. I'll just do a messagebox
                tkinter.messagebox.showerror('Dafuq', "Something went really wrong in the .steal_button_click, brah =(")
            self.controller.show_frame(MainPage)
        else:
            # nothing selected, just ignore this shit
            return -1


# Class for storing, loading, saving and displaying settings. Utilizes json module
class Settings(object):
    # headers = list of names of files/categories for settings, body is a list of dictionaries
    # settings are stored in .json files in \settings\ folder
    headers = []
    body = []
    directory = getcwd() + "\Settings\\"

    def load_from_file(self, filename):
        name, ext = splitext(path.basename(filename))
        self.headers.append(name)
        with open(filename, "r") as file:
            temp_dict = json.load(file)
        self.body.append(temp_dict)

    def load_from_folder(self):
        self.headers = []
        self.body = []
        folder = self.directory
        for entry in scandir(folder):
            name, ext = splitext(entry.path)
            if ext == ".json":
                self.load_from_file(entry.path)

    def dict_by_name(self, dict_name):
        index = self.headers.index(dict_name)
        return self.body[index]

    def add_setting_by_dict_name(self, name, key, value):
        index = self.headers.index(name)
        self.body[index][key] = value

    def save_to_folder(self):
        for name in self.headers:
            temp_dict = self.dict_by_name(name)
            fullpath = self.directory + name + ".json"
            print("Saving %s to %s" % (name, fullpath))
            with open(fullpath, "w") as file:
                json.dump(temp_dict, file)

    # Visualizes settings in a tkinter window.


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
                    answer = tkinter.messagebox.askquestion('Whatchagonnado', temp_text)
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
            if (entry.name[0] != "!") and entry.is_dir():
                # titles will include [ and ] for distrib_source, we ignore them for title and parse them for source
                if entry.name.find('[') >= 0:
                    game_title = remove_extra_spaces_from_string(entry.name[0:entry.name.find('[')])
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
                new_game = Game(game_title, version, folder, installer, distrib_type)
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
            tkinter.messagebox.showinfo('Results', "No duplicates found in your library!")
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


# This class will hopefully contain methods to login into sites and get magnet links / torrent files from those
class TPBUser(object):
    url = "https://thepiratebay.org"

    # 0/99/401 = unknown(relevancy?)/torrents availability?/category(games -> PC)
    def construct_search_url(self, game_name):
        return "%s/search/%s/0/99/401" % (self.url, game_name)

    # Returns a list of torrents from TPB for a game name
    def get_torrents(self, game_name):
        r = requests.get(self.construct_search_url(game_name))
        return self.parse_search_result(r.text)

    # This will take a result from a http requests and return a list of torrents (objects)
    def parse_search_result(self, result):
        list_of_torrents = []
        # take unnecessary shit in front of torrents
        temp = result
        temp = temp[temp.find('Search results:'):]
        temp = temp[temp.find('<td>')+4:]
        # take unnecessary shit in the end
        temp = temp[:temp.find('<div class="ads"')]
        # parse torrents payload
        while temp.find('div class="detName"') != -1:
            temp = temp[temp.find('div class="detName"')+19:]
            temp = temp[temp.find('title="Details for ') + 19:]
            tname = temp[:temp.find("\"")]
            temp = temp[temp.find('<a href="magnet') + 9:]
            tlink = temp[:temp.find('title="Download this torrent using magnet"')-2]
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
            temp_torrent = Torrent(tlink, tname, tsize, tseeds, tleeches, tsite)
            # Only add a torrent if there is at least 1 seeder
            if tseeds >= 1:
                list_of_torrents.append(temp_torrent)
        return list_of_torrents


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
            LOGIN_DATA = dict(login_username=USERNAME, login_password=PASSWORD, login=WTF)
            s.post(URL, data=LOGIN_DATA, headers={'Referer': 'http: // tapochek.net / index.php'})
            self.try_test_url()
        return None


# This class will hopefully work with freegogpcgames.com
class FreeGOGPCUser(object):
    url = 'http://freegogpcgames.com'

    # construct the search url
    def construct_search_url(self, game_name):
        return "%s/?s=%s" % (self.url, game_name)

#     def test_FreeGOGPC(self, game_name, file_name):
#         r = requests.get(self.construct_search_url(game_name))
#         print("I ve requested %s" % self.construct_search_url(game_name))
# #        with open(file_name, 'wb') as file:
# #           file.write(self.parse_search_result(r.text).encode('utf-8', errors='replace'))
#         for i in self.parse_search_result(r.text):
#             print(i.as_list())

    def get_torrents(self, game_name):
        r = requests.get(self.construct_search_url(game_name))
        return self.parse_search_result(r.text)

    def parse_search_result(self, result):
        temp = result
        list_of_torrents = []
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
            temp_torrent = Torrent(tlink2, tname, tsize, 999, 999, 'FreeGOGPCGames')
            list_of_torrents.append(temp_torrent)
        return list_of_torrents

my_tpb = TPBUser()
my_FreeGOG = FreeGOGPCUser()
my_Tapochek = TapochekUser()
my_Tapochek.try_login()
my_lib = GameLibrary()
app = MainApp()
app.mainloop()
