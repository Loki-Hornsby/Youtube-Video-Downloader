# ----- Compile Command ----- #
# pyinstaller -w --onefile DownloadApp.pyw
# https://www.youtube.com/watch?v=6PKdX1n5wn8

from __future__ import print_function, unicode_literals

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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

class Window(QWidget):
    # Download Stage
    DownloadStage = 0

    def __init__(self):
            super().__init__()

            # calling initUI method
            self.initUI()

            # Entry
            #self.sv = StringVar()
            #self.sv.trace("w", lambda name, index, mode, sv = self.sv: self.callback(self))
            
            #self.entry = tk.Entry(root, textvariable = self.sv)
            #self.canvas.create_window(200, 140, window = self.entry)

    # method for creating widgets
    def initUI(self):
            self.setGeometry(300, 300, 280, 170)
            self.setWindowTitle("Youtube Downloader")
        
            self.pbar = QProgressBar(self)
            self.pbar.setGeometry(30, 40, 200, 25)

            self.btn = QPushButton('Start', self)
            self.btn.move(40, 80)
            #self.btn.clicked.connect(self.doAction)

            # showing all the widgets
            self.show()


    def Download(self, args):
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

    def UpdateStage(self, args):
        self.DownloadStage += 1
        print("Changing State to " + str(self.DownloadStage))

    def CancelDownload(self, ind, args):
        print(self.ListIndex)
        print(ind)
    
    def callback(self, args):
        self.Link = self.sv.get()
        
        if len(self.Link) > 0:
            try:
                self.SongName = YouTube(self.Link).title

                #self.entry.config(state="disable")

                self.entry.delete(0, 'end')

                self.UpdateStage(self)
            except:
                self.entry.config(fg='red')  
        
# Main
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
  
    # create the instance of our Window
    window = Window()
  
    # start the app
    sys.exit(App.exec())


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
