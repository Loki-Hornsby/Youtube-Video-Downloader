# ----- Compile Command ----- #
# pyinstaller -w --onefile DownloadApp.pyw
# https://www.youtube.com/watch?v=6PKdX1n5wn8

from __future__ import print_function, unicode_literals

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time
import clipboard

import sys
from sys import argv  
from subprocess import call            

from pytube import YouTube
from pytube.helpers import safe_filename
import youtube_dl

import sys
import os
from winreg import *

# Download
with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
    Downloads = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        print("Thread Started...")
        self.fn(*self.args, **self.kwargs)
        print("Thread Ended")
        
class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
            
        self.initUI()

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("Youtube Downloader")
        layout = QGridLayout()
        layout.setColumnStretch (0, 1)
        layout.setRowStretch (0, 0)
        
        # |0,0|0,1|0,2|0,3|
        # |1,0|1,1|1,2|1,3|
        # |2,0|2,1|2,2|2,3|
        # |3,0|3,1|3,2|3,3|
        
        layout.addWidget(self.Entry, 0,0)
        layout.addWidget(self.pbar,  1,0)
        layout.addWidget(self.btn,   1,1)
            
        self.horizontalGroupBox.setLayout(layout)

    def GetSongName(self):
        try:
            self.SongName = YouTube(self.Link).title
        except:
            print("Incorrect Name :)")
            
        #self.Download(self)

    def callback(self):
        self.Link = self.Entry.text()
    
        if len(self.Link) > 0:
            print(self.Link)

            worker = Worker(self.GetSongName)
            self.threadpool.start(worker)
            
            #self.Entry.setEnabled(False)
            #self.Entry.clear()

    # method for creating widgets
    def initUI(self):
        # Window Setup
        self.setFixedSize(400, 0)
        self.center()
        self.setWindowTitle("Youtube Downloader")

        # Progress Bar
        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.pbar.adjustSize()
      
        # Button
        self.btn = QPushButton('X', self)
        self.btn.setToolTip("Remove 'Song Title Goes Here'")
     
        #self.btn.clicked.connect(self.doAction)

        # Entry
        self.Entry = QLineEdit(self)
        self.Entry.setPlaceholderText("Paste A Youtube Link Here")
        self.Entry.setStyleSheet("color: rgb(0, 0, 0);")
        self.Entry.textChanged.connect(self.callback)
            
        # Layout
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        # showing all the widgets
        self.show()

        print("Ui Setup!")

    def DownloadHook(self, d):
        if d['status'] == 'downloading':
            p = d['_percent_str']
            p = p.replace('%','')
            #self.pbar.setValue(int(p))
            print(p)

    def Download(self, args):
        self.ydl_opts = {
            'outtmpl': Downloads + '\\' + self.SongName + '.%(ext)s',
            'format': 'bestaudio/best',
            'progress_hooks': [self.DownloadHook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
            ],
        }
        
        #youtube_dl.YoutubeDL(self.ydl_opts).download([self.Link])

    def CancelDownload(self, ind, args):
        print(self.ListIndex)
        print(ind)
        
# Main
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
  
    # create the instance of our Window
    window = Window()
  
    # start the app
    sys.exit(App.exec_())

'''
# Data
Link = clipboard.paste()

global Name

try:
    Name = YouTube(Link).title

    DownloadStage = 1
except:
    ctypes.windll.user32.MessageBoxW(0, "Incorrect link", "Proccess Failed", Ontop | Error)
    sys.exit("Incorrect Link")

# Download Query
def DownloadQuery():
    result = ctypes.windll.user32.MessageBoxW(0, "Download " + Name + "?", "Download?", Ontop | Question)
     
    if result == IDNO:
        sys.exit("User Cancelled Download")

    if result != IDYES:
        sys.exit("Malform?")

DownloadQuery()

# Main Loop
while True:
    if DownloadStage == 1:
        print("Downloading")
     
        ydl_opts = {
            'outtmpl': Downloads + '\\' + Name + '.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
            ],
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([Link])


        DownloadStage = 2

    if DownloadStage == 2:
        ctypes.windll.user32.MessageBoxW(0, "Proccess finished succesfully", "Finished", Ontop | Error)
        sys.exit("Finished")

        DownloadStage = 0
'''
