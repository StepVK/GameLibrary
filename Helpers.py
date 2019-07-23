from os import scandir
from os import startfile
from os.path import splitext
import tkinter

# removes extra spaces at the beginning and end of a string
list_of_valid_installer_types = [".exe", '.iso']


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
