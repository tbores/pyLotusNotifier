pyLotusNotifier
===============

Lotus Notes Email Notifier

This software uses the COM interface of Lotus Notes for accessing your Email Database.

Build
-----

pyLotusNotifier is written in python-32bits-3.3.2
You need the following dependencies:
* pyside
* pywin32

The best way is to install WinPython-32bit-3.3.2.3 available [here](http://code.google.com/p/winpython/downloads/list)

If you have installed WinPython-32bit-3.3.2.3 in c:\ then you can use build_for_win32.bat file to generate a windows executable.

User guide
----------
* When pyLotusNotifier starts, no window open, the software is directly minimized to your system tray
* Make a right click on the system tray icon to open pyLotusNotifier menu
* Click on Configure in the menu to configure the access to your Lotus Email
* You need to fill the following information in the configuration dialog:
    * Server Name
    * Path to the .nsf file
    * Password


