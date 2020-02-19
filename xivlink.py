#!/usr/bin/env python

import ctypes
import datetime
from pathlib import Path, PurePath
import os
import shutil


def confirm_authorization():
    try:
        is_admin = True
        _ = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if not is_admin:
        print("This program requires administrator access to work correctly. Please re-run as administrator.")
        exit()


def get_character_directory():
    # Attempt to find character directories.
    done = False
    home = Path.home()
    candidate_dir_parent = PurePath.joinpath(
        home, "Documents", "My Games", "FINAL FANTASY XIV - A Realm Reborn")
    candidate_dirs = os.listdir(candidate_dir_parent)
    candidate_dirs = [d for d in candidate_dirs if d.find("FFXIV_CHR") >= 0 and d.find("backup") == -1]
    if len(candidate_dirs) >= 1:
        candidate_dir = [PurePath.joinpath(candidate_dir_parent, d)
                         for d in candidate_dirs]
        candidate_dir_rel = [p.name for p in candidate_dir]
        query = "Found candidate directories:\n"
        for d in candidate_dir:
            query += "- " + str(d) + "\n"
        query += "Use all of these directories?\n"
        if len(candidate_dirs) == 1:
            query = "Found candidate directory:\n- " + str(candidate_dir[0]) + "\nUse this directory?\n"
        use_candidate = ask_yes_no_quit(query)
        if use_candidate:
            return candidate_dir, candidate_dir_rel

    # No character directories found. Prompt for one.
    query = "Enter path to character directory:\n"
    while not done:
        char_dir = Path(input(query))
        char_dir_rel = PurePath(char_dir).name
        if Path.exists(char_dir):
            done = True
        else:
            print("Character directory not found. Character directories usually look like C:\\Users\\xxxxxxxx\\Documents\\My Games\\FINAL FANTASY XIV - A Realm Reborn\\FFXIV_CHRxxxxxxxxxxxxxxxx\n")
    return [char_dir], [char_dir_rel]


def get_share_directory():
    # Attempt to find Dropbox.
    done = False
    home = Path.home()
    potential_dropbox = PurePath.joinpath(home, "Dropbox")
    if Path.exists(potential_dropbox):
        query = "Synchronize using Dropbox found at " + str(potential_dropbox) + "?\n"
        use_dropbox = ask_yes_no_quit(query)
        if use_dropbox:
            return potential_dropbox

    # No Dropbox found. Prompt for a shared folder.
    done = False
    query = "Enter path to a shared folder for synchronization:\n"
    while not done:
        share_dir_path = input(query)
        share_dir = Path(share_dir_path)
        if Path.exists(share_dir):
            done = True
        else:
            print(
                "Shared folder not found. Shared folders usually look like C:\\Users\\xxxxxxxx\\Dropbox\n")
        return share_dir


def ask_about_copying_ui():
    query = "Copy UI layout (will break UI if not all systems' display resolutions match)?\n"
    copy_ui = ask_yes_no_quit(query)
    return copy_ui


def create_links(char_dirs, char_dirs_rel, share_dir, copy_ui):
    result = "none"
    for char_dir, char_dir_rel in zip(char_dirs, char_dirs_rel):
        if Path.exists(char_dir) and Path.exists(share_dir):
            result = "failure"
            destination = PurePath.joinpath(share_dir, char_dir_rel)
            backup_dir = Path(str(char_dir) + '-backup-' + \
                str(datetime.datetime.now().date()))
            if Path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(char_dir, backup_dir)
            if copy_ui:
                if not Path.exists(destination):
                    shutil.move(char_dir, destination)    
                os.symlink(destination, char_dir, target_is_directory=True)
                result = "success"
            else:
                if not Path.exists(destination):
                    Path.mkdir(destination)
                for f in os.listdir(char_dir):
                    if f.upper().startswith("ADDON"):
                        continue
                    shutil.move(PurePath.joinpath(char_dir, f), PurePath.joinpath(share_dir, char_dir_rel, f))
                    os.symlink(PurePath.joinpath(share_dir, char_dir_rel, f), PurePath.joinpath(char_dir, f))
                    result = "success"
    if result == "success":
        print("Created links successfully. Run this program once on each system you wish to synchronize.")
    elif result == "failure":
        print("Failed to create links. To avoid the risk of damaging your data, the program will exit without doing anything.")
    elif result == "none":
        print("Couldn't find any actions to take. The program will now exit.")


def ask_yes_no_quit(query):
    done = False
    while not done:
        user_input = input(query)
        if user_input.lower().startswith('y'):
            answer = True
            done = True
        elif user_input.lower().startswith('n'):
            answer = False
            done = True
        elif user_input.lower().startswith('q'):
            exit()
        else:
            query = "Invalid input. Please type yes/no/quit\n"
            continue
    return answer


def main():
    confirm_authorization()
    char_dirs, char_dir_rel = get_character_directory()
    share_dir = get_share_directory()
    copy_ui = ask_about_copying_ui()
    create_links(char_dirs, char_dir_rel, share_dir, copy_ui)


if __name__ == "__main__":
    main()
