import tkinter.messagebox
from tkinter import *
from tkinter.ttk import Scrollbar, Treeview

from Classes.FreeGOGPCUser import FreeGOGPCUser
from Classes.Game import Game
from Classes.GameLibrary import GameLibrary
from Classes.TapochekUser import TapochekUser
from Classes.Torrent import Torrent
from Classes.TPBUser import TPBUser
from Helpers import fill_tv_from_list
from Helpers import launch_installer

# Global variables

global_version = 0.1


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
        tv.grid(row=0, column=0, rowspan=10,
                columnspan=10, sticky=(N, E, W, S))
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

        settings_button = Button(
            self, text="Settings", command=lambda: controller.show_frame(SettingsPage))
        settings_button.grid(row=10, column=0, sticky=N + S + E + W)

        populate_button = Button(self, text="Load library",
                                 command=lambda: fill_tv_from_list(tv, my_lib.as_list(), 3))
        populate_button.grid(row=10, column=1, sticky=N + S + E + W)

        install_button = Button(self, text="Install game",
                                command=lambda: self.installer_page_button(
                                    my_lib.install_game(tv.item(tv.focus())['text'])))
        install_button.grid(row=10, column=2, sticky=N + S + E + W)

        duplicates_button = Button(
            self, text="Find duplicates", command=my_lib.find_duplicates)
        duplicates_button.grid(row=10, column=3, sticky=N + S + E + W)

        search_entry = Entry(self, text="")
        search_entry.grid(row=10, column=4, columnspan=3, sticky=N + S + E + W)
        self.torrent_search_entry = search_entry

        search_button = Button(self, text="Find in library", command=lambda: fill_tv_from_list(
            tv, my_lib.find_games_by_name(search_entry.get()).as_list(), 3))
        search_button.grid(row=10, column=7, sticky=N + S + E + W)

        # TODO Make this to look on more different torrents

        torrent_button = Button(
            self, text="Find on torrents", command=self.torrent_button_on_click)
        torrent_button.grid(row=10, column=8, sticky=N + S + E + W)

        quit_button = Button(self, text="Quit", command=controller.destroy)
        quit_button.grid(row=10, column=9, sticky=N + S + E + W)

    # It will clear the torrent page treeview, upload a new torrent list into current tor list on page, then call the
    # fill_treeview function to display shit and make the page visible
    def torrent_button_on_click(self):
        torrent_list = my_tpb.get_torrents(self.torrent_search_entry.get())
        torrent_list += my_FreeGOG.get_torrents(
            self.torrent_search_entry.get())
        if len(torrent_list) == 0:
            # There are no torrents
            tkinter.messagebox.showinfo(
                'No luck', "Sorry, no torrents have been found =(")
        else:
            # Some were found, let's proceed
            self.controller.show_frame(TorrentsPage)
            t_page = self.controller.get_page('TorrentsPage')
            t_page.torrents_treeview.delete(
                *t_page.torrents_treeview.get_children())
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
                    self.controller.get_page(
                        'MultipleInstallPage').temp_tv.insert('', 'end', text=item)
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
        temp_tv.grid(row=0, column=0, rowspan=3,
                     columnspan=4, sticky=(N, E, W, S))
        temp_tv.heading('#0', text="Choose one:")
        temp_tv.column("#0", minwidth=300)

        # adding scrollbar

        ysb = Scrollbar(self, orient='vertical', command=temp_tv.yview)
        temp_tv.configure(yscroll=ysb.set)
        ysb.grid(row=0, column=3, rowspan=3, sticky='nse')

        # Buttons for the rest

        ok_button = Button(self, text="Ok", command=self.ok_button_click)
        ok_button.grid(row=3, column=0, sticky=N + S + E + W)

        cancel_button = Button(self, text="Cancel",
                               command=lambda: controller.show_frame(MainPage))
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

        paths_label = Label(
            self, text="PATHS OF YOUR GAME LIBRARY", font=('Fixedsys', 16))
        paths_label.grid(row=0, column=0, columnspan=10, sticky=N + S + E + W)

        # TODO: Make these buttons do stuff? :D
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

        cancel_button = Button(self, text="Cancel",
                               command=lambda: controller.show_frame(MainPage))
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
        torrents_treeview.grid(row=0, column=0, rowspan=3,
                               columnspan=4, sticky=(N, E, W, S))
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

        ysb = Scrollbar(self, orient='vertical',
                        command=torrents_treeview.yview)
        torrents_treeview.configure(yscroll=ysb.set)
        ysb.grid(row=0, column=3, rowspan=3, sticky='nse')

        # Buttons for the rest

        steal_button = Button(self, text="Steal that shit!",
                              command=self.steal_button_click)
        steal_button.grid(row=3, column=0, sticky=N + S + E + W)

        cancel_button = Button(self, text="Cancel",
                               command=lambda: controller.show_frame(MainPage))
        cancel_button.grid(row=3, column=3, sticky=N + S + E + W)

    # Will identify the torrent by it's name and site (hopefully enough?), find it in the current torrents which was
    # populated by the main page button and invoke the .download in the torrent class. Then will just show the main page
    def steal_button_click(self):
        # probably only should do stuff when something is selected
        if self.torrents_treeview.focus() != '':
            torrent_name = self.torrents_treeview.item(
                self.torrents_treeview.focus())['text']
            torrent_from = self.torrents_treeview.item(
                self.torrents_treeview.focus())['values'][2]
            for torrent in self.current_torrents_list:
                if torrent.name == torrent_name and torrent.site == torrent_from:
                    torrent.download_torrent()
                    break
            else:
                # Weird, seems like the torrent couldn't be found. I'll just do a messagebox
                tkinter.messagebox.showerror(
                    'Dafuq', "Something went really wrong in the .steal_button_click, brah =(")
            self.controller.show_frame(MainPage)
        else:
            # nothing selected, just ignore this shit
            return -1


my_tpb = TPBUser()
my_FreeGOG = FreeGOGPCUser()
my_Tapochek = TapochekUser()
my_Tapochek.try_login()
my_lib = GameLibrary()
app = MainApp()
app.mainloop()
