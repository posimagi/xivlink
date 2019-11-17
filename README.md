# xivlink

A tool for semi-permanently synchonizing your Final Fantasy XIV character and UI settings across multiple systems.

## System Requirements

* You must have Python 3.5 or newer (https://www.python.org/downloads/).
* You need some kind of shared storage. I recommend using a Dropbox folder for automatic synchronization, but even something as simple as a flash drive that you take with you and leave in your active system will work.

## How to Use

`xivlink` can be invoked in either of two ways

* run `xivlink.py` as administrator, with an applicable version of Python in your `PATH`
* open an elevated command prompt, e.g. by right-clicking on Start and then clicking "Command Prompt (Admin)", navigate to the directory containing `xivlink.py`, and then run `python xivlink.py`

## Notes

### A word about ADDON.DAT

`ADDON.DAT` stores your HUD Layout. Synchronizing it across machines will do exactly what you want... unless they have different screen resolutions, in which case it will most definitely not do what you want. Answering "no" to the third question will exclude it from synchronization for this purpose, although it does mean you'll have to edit your HUD separately on each device.

### Why are Administrator privileges required?

Unfortunately, Windows requires Administrator privileges to create symlinks. On macOS and Linux, root privileges should not be necessary.

### *Semi*-permanent?

Running this tool once on each machine on which you play should keep their settings synchronized forever, but there's no guarantee that the internal structure of the user data directory won't be changed at some point in the future. If that happens, the synchronization may or may not continue to work, and re-running it without an update to the tool itself may or may not be sufficient to restore synchronization. The future is so exciting!

### Compatibility

This program is tested only on Windows 10. It may work on other systems anyway. It is not guaranteed to work, nor supported, on any system. Always make a backup of anything you don't want to lose before running applications you downloaded from the internet.

## Special Thanks

A special shout-out to friends over at the Crystal Data Center Discord who inspired me to create this. Come by and say hi! https://discord.gg/CXTvAGq