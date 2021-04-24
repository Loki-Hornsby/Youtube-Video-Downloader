# ----- Compile Command ----- #
# pyinstaller -w --onefile DownloadApp.pyw
# https://www.youtube.com/watch?v=6PKdX1n5wn8

from __future__ import print_function, unicode_literals

from subprocess import call            
from sys import argv  
from pytube import YouTube
from pytube.helpers import safe_filename
import clipboard
from tkinter import *
from tkinter import messagebox, Toplevel
import tkinter as tk
import sys
import os
from winreg import *
import youtube_dl

# Ctypes
import ctypes

IDYES = 6
IDNO = 7
Ontop = 0x1000

Error = 0x10
Question = 0x40

# Download
with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
    Downloads = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

class Window:
    # Download Stage
    DownloadStage = 0

    # Index
    ListIndex = 0

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
    
    def hide_me(self, event, args):
        event.widget.place_forget()

    def UpdateStage(self, args):
        self.DownloadStage += 1
        print("Changing State to " + str(self.DownloadStage))

    def CancelDownload(self, ind, args):
        #self.entry.config(state="normal")
        #self.entry.delete(0, 'end')
        print(self.ListIndex)
        print(ind)
        
        self.SongLabels[ind].destroy()
        self.CancelButtons[ind].destroy()

    def CreateTag(self, args):
        self.ChangingString = "..."
        self.songLabel = tk.Label(root, text='Downloading ' + self.SongName + self.ChangingString)
        self.songLabel.config(font=('helvetica', 10))
        self.canvas.create_window(200, 180, window = self.songLabel)
        
        self.cancel = tk.Button(text='X', command = lambda : self.CancelDownload(self, self.ListIndex), bg='brown', fg='white', font=('helvetica', 9, 'bold'))
        self.canvas.create_window(220, 180, window = self.cancel)

        self.CancelButtons.append(self.cancel)
        self.SongLabels.append(self.songLabel)

        self.ListIndex += 1
    
    def callback(self, args):
        self.Link = self.sv.get()
        
        if len(self.Link) > 0:
            try:
                self.SongName = YouTube(self.Link).title

                #self.entry.config(state="disable")

                self.entry.delete(0, 'end')

                self.CreateTag(self)

                self.UpdateStage(self)
            except:
                self.entry.config(fg='red')

    def __init__(self, args):
        # Lists
        self.CancelButtons = []
        self.SongLabels = []
        
        # Canv
        self.canvas = tk.Canvas(root, width = 400, height = 300,  relief = 'raised')
        self.canvas.pack()

        # Labels
        self.label1 = tk.Label(root, text='Audio Downloader')
        self.label1.config(font=('helvetica', 14))
        self.canvas.create_window(200, 25, window = self.label1)

        self.label2 = tk.Label(root, text='Paste Link Here')
        self.label2.config(font=('helvetica', 10))
        self.canvas.create_window(200, 100, window = self.label2)

        # Entry
        self.sv = StringVar()
        self.sv.trace("w", lambda name, index, mode, sv = self.sv: self.callback(self))
        
        self.entry = tk.Entry(root, textvariable = self.sv)
        self.canvas.create_window(200, 140, window = self.entry)

        # Cancel
        #if self.DownloadStage == 1:
        
# Main
root = tk.Tk()
wind = Window(root)
root.mainloop()

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
