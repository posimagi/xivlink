# xivlink

A tool for semi-permanently synchonizing your Final Fantasy XIV settings across multiple systems.

## System Requirements

You must have Python 3.5 or newer (https://www.python.org/downloads/).

## How to Use

`xivlink` can be invoked in either of two ways

* run `xivlink.py` as administrator, with an applicable version of Python in your `PATH`
* open an elevated command prompt, e.g. by right-clicking on Start and then clicking "Command Prompt (Admin)"

### A word about ADDON.DAT

`ADDON.DAT` stores your HUD Layout. Synchronizing it across machines will do exactly what you want... unless they have different screen resolutions, in which case it will most definitely not do what you want. Answering "no" to the third question will exclude it from synchronization for this purpose, although it does mean you'll have to edit your HUD separately on each device.

### Why are Administrator privileges required?

Unfortunately, Windows requires Administrator privileges to create symlinks. On macOS and Linux, root privileges should not be necessary.

## Miscellany

This program is tested only on Windows 10. It may work on other systems anyway. It is not guaranteed to work, nor supported, on any system. Always make a backup of anything you don't want to lose before running applications you downloaded from the internet.

## Special Thanks

A special shout-out to friends over at the Crystal Data Center Discord who inspired me to create this. Come by and say hi! https://discord.gg/CXTvAGq