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
        if hasattr(ctypes, "windll"):
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            print("The program could not determine your OS and cannot safely proceed.")
            exit()
    if not is_admin:
        print(
            "This program requires administrator access to work correctly. Please re-run as administrator."
        )
        exit()


def get_character_directory():
    # Attempt to find character directories.
    done = False
    char_dir = None
    char_dir_rel = None
    home = Path.home()
    candidate_dir_parent = PurePath.joinpath(
        home, "Documents", "My Games", "FINAL FANTASY XIV - A Realm Reborn"
    )

    try:
        candidate_dirs = os.listdir(candidate_dir_parent)
    except FileNotFoundError:
        print(
            "Character directory path not found. You'll need to provide the path manually."
        )
        candidate_dirs = []
    except PermissionError:
        print("Permission denied accessing character directory path.")
        candidate_dirs = []

    candidate_dirs = [
        d for d in candidate_dirs if d.find("FFXIV_CHR") >= 0 and d.find("backup") == -1
    ]
    if len(candidate_dirs) >= 1:
        candidate_dir = [
            PurePath.joinpath(candidate_dir_parent, d) for d in candidate_dirs
        ]
        candidate_dir_rel = [p.name for p in candidate_dir]
        query = "Found candidate directories:\n"
        for d in candidate_dir:
            query += "- " + str(d) + "\n"
        query += "Use all of these directories?\n"
        if len(candidate_dirs) == 1:
            query = (
                "Found candidate directory:\n- "
                + str(candidate_dir[0])
                + "\nUse this directory?\n"
            )
        use_candidate = ask_yes_no_quit(query)
        if use_candidate:
            return candidate_dir, candidate_dir_rel

    # No character directories found. Prompt for one.
    query = "Enter path to character directory:\n"
    while not done:
        char_dir = Path(input(query))
        char_dir_rel = PurePath(char_dir).name
        if Path.exists(char_dir):
            if not Path.is_dir(char_dir):
                print("Path exists but is not a directory.\n")
                continue
            done = True
        else:
            print(
                "Character directory not found. Character directories usually look like C:\\Users\\xxxxxxxx\\Documents\\My Games\\FINAL FANTASY XIV - A Realm Reborn\\FFXIV_CHRxxxxxxxxxxxxxxxx\n"
            )
    return [char_dir], [char_dir_rel]


def get_share_directory():
    # Attempt to find Dropbox.
    done = False
    share_dir = None
    home = Path.home()
    potential_dropbox = Path.joinpath(home, "Dropbox")
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
            if not Path.is_dir(share_dir):
                print("Path exists but is not a directory.\n")
                continue
            done = True
        else:
            print(
                "Shared folder not found. Shared folders usually look like C:\\Users\\xxxxxxxx\\Dropbox\n"
            )
            continue
    return share_dir


def ask_about_copying_ui():
    query = "Copy UI layout (will break UI if not all systems' display resolutions match)?\n"
    copy_ui = ask_yes_no_quit(query)
    return copy_ui


def create_links(char_dirs, char_dirs_rel, share_dir, copy_ui):
    result = "none"
    for char_dir, char_dir_rel in zip(char_dirs, char_dirs_rel):
        if not Path.exists(char_dir):
            print(
                f"Warning: character directory {char_dir} no longer exists. Skipping."
            )
            continue
        if not Path.exists(share_dir):
            print(f"Error: share directory {share_dir} does not exist.")
            result = "failure"
            break

        try:
            result = "failure"
            destination = Path(share_dir) / char_dir_rel
            backup_timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
            backup_dir = Path(str(char_dir) + "-backup-" + backup_timestamp)

            # Safely remove existing backup with exception handling
            if Path.exists(backup_dir):
                try:
                    shutil.rmtree(backup_dir)
                except OSError as e:
                    print(
                        f"Warning: Could not remove existing backup at {backup_dir}: {e}"
                    )
                    continue

            # Create backup
            try:
                shutil.copytree(char_dir, backup_dir)
            except OSError as e:
                print(f"Error: Could not create backup at {backup_dir}: {e}")
                continue

            if copy_ui:
                if not Path.exists(destination):
                    try:
                        shutil.move(str(char_dir), str(destination))
                    except OSError as e:
                        print(f"Error: Could not move directory to {destination}: {e}")
                        continue
                try:
                    os.symlink(destination, char_dir, target_is_directory=True)
                    result = "success"
                except OSError as e:
                    print(f"Error: Could not create symlink at {char_dir}: {e}")
                    continue
            else:
                if not Path.exists(destination):
                    try:
                        Path.mkdir(destination, parents=True, exist_ok=True)
                    except OSError as e:
                        print(
                            f"Error: Could not create destination directory {destination}: {e}"
                        )
                        continue

                # Validate and move files (with rollback on error)
                files_to_move = []
                try:
                    for f in os.listdir(char_dir):
                        if f.upper().startswith("ADDON"):
                            continue
                        src = Path(char_dir) / f
                        # Security: Don't follow symlinks
                        if src.is_symlink():
                            print(f"Warning: Skipping symlink {src}")
                            continue
                        files_to_move.append(f)
                except OSError as e:
                    print(f"Error: Could not list directory {char_dir}: {e}")
                    continue

                # Move files one by one with error handling
                files_moved = []
                for f in files_to_move:
                    try:
                        src = Path(char_dir) / f
                        dst = Path(destination) / f
                        shutil.move(str(src), str(dst))
                        src_link = Path(char_dir) / f
                        os.symlink(dst, src_link, target_is_directory=src.is_dir())
                        files_moved.append(f)
                        result = "success"
                    except OSError as e:
                        print(f"Error: Could not move {f}: {e}")
                        # Don't continue on individual file failures, but note it
                        continue

                if not files_moved:
                    print(f"Warning: No files were moved for {char_dir_rel}")
                    result = "failure"

        except Exception as e:
            print(f"Unexpected error processing {char_dir}: {e}")
            result = "failure"

    if result == "success":
        print(
            "Created links successfully. Run this program once on each system you wish to synchronize."
        )
    elif result == "failure":
        print(
            "Failed to create links. To avoid the risk of damaging your data, the program will exit without doing anything."
        )
    elif result == "none":
        print("Couldn't find any actions to take. The program will now exit.")


def ask_yes_no_quit(query):
    answer = False
    done = False
    while not done:
        user_input = input(query)
        if user_input.lower().startswith("y"):
            answer = True
            done = True
        elif user_input.lower().startswith("n"):
            answer = False
            done = True
        elif user_input.lower().startswith("q"):
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
