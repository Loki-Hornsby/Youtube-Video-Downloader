"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ["DownloadApp.pyw"]
DATA_FILES = ['DownloadApp.pyw', 'output log/LOG.txt']
OPTIONS = {}

setup(
    app=APP,
    name = "DownloadApp",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app', 'pytube', "pyqt5", "clipboard"],
)
