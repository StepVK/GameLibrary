import json
from os import getcwd, path, scandir
from os.path import splitext

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
