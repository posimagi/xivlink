#!/usr/bin/env python

import ctypes
import datetime
import os
import shutil

try:
    is_admin = true
    _ = os.getuid() == 0
except AttributeError:
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
if not is_admin:
    print("This program requires administrator access to work correctly. Please re-run as administrator.")
    exit()

done = False
query = "Enter path to character directory:\n"
while not done:
    char_dir = input(query)
    char_dir_rel = os.path.basename(char_dir)
    if os.path.exists(char_dir):
        done = True
    else:
        print("Character directory not found. Character directories usually look like C:\\Users\\xxxxxxxx\\Documents\\My Games\\FINAL FANTASY XIV - A Realm Reborn\\FFXIV_CHRxxxxxxxxxxxxxxxx\n")

done = False
query = "Enter path to a shared folder, such as Dropbox:\n"
while not done:
    share_dir = input(query)
    if os.path.exists(share_dir):
        done = True
    else:
        print("Shared folder not found. Shared folders usually look like C:\\Users\\xxxxxxxx\\Dropbox\n")

done = False
query = "Copy UI layout (will break UI if not all systems' display resolutions match)?\n"
while not done:
    copy_input = input(query)
    print(copy_input)
    if copy_input.lower().startswith('y'):
        copy_ui = True
        done = True
    elif copy_input.lower().startswith('n'):
        copy_ui = False
        done = True
    elif copy_input.lower().startswith('q'):
        exit()
    else:
        query = "Invalid input. Please type yes/no/quit\n"
        continue

if os.path.exists(char_dir) and os.path.exists(share_dir):
    backup_dir = char_dir + '-backup-' + str(datetime.datetime.now().date())
    shutil.copytree(char_dir, backup_dir)
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    if copy_ui:
        if not os.path.exists(os.path.join(share_dir, char_dir_rel)):
            shutil.move(char_dir, os.path.join(share_dir, char_dir_rel))
        os.symlink(os.path.join(share_dir, char_dir_rel), char_dir)
    else:
        if not os.path.exists(os.path.join(share_dir, char_dir_rel)):
            os.mkdir(os.path.join(share_dir, char_dir_rel))
        for f in os.listdir(char_dir):
            if f.upper().startswith("ADDON"):
                continue
            shutil.move(os.path.join(char_dir, f), os.path.join(
                share_dir, char_dir_rel, f))
            os.symlink(os.path.join(share_dir, char_dir_rel, f),
                       os.path.join(char_dir, f))
    print("Created links successfully. Run once on each system you wish to synchronize.")
