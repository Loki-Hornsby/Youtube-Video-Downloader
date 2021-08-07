# ----- Compile Command ----- #
# pyinstaller -w --onefile DownloadApp.pyw

from __future__ import print_function, unicode_literals
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pytube import YouTube
from pytube import Playlist

import sys
import subprocess

import os
from winreg import *
import glob
import traceback
import uuid

import clipboard
import timeit

from win10toast import ToastNotifier
toaster = ToastNotifier()

with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
    Download = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

DownloadLocation = Download


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
        

class Window(QWidget):

    
    def __init__(self):
        super(Window, self).__init__()

        # Error Occured
        self.ErrorOccured = False

        # Initialize Ui
        self.initUI()

        # Setup Threads
        self.threads = 0
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
        
        layout.setColumnStretch (1, 1)
        layout.setRowStretch (1, 0)
        layout.setColumnStretch (2, 0)
        
        # |0,0|0,1|0,2|0,3|
        # |1,0|1,1|1,2|1,3|
        # |2,0|2,1|2,2|2,3|
        # |3,0|3,1|3,2|3,3|

        layout.addWidget(self.DCount,           0,0)
        layout.addWidget(self.downloadbtn,      0,1)
        layout.addWidget(self.locationbtn,      0,2)
        layout.addWidget(self.Loading,          0,3)
        
        self.horizontalGroupBox.setLayout(layout)


    def PopUp(self):
        # Finishing Popup
        if self.ErrorOccured == False:
            toaster.show_toast("Threads Complete!",
                "all songs have been downloaded!",
                icon_path="Logo.ico",
                duration=40,
                threaded=True)


    def thread_complete(self):
        # Threads
        self.threads -= 1
        self.DCount.setText(str(self.threads))

        # No Threads Left Condition
        if self.threads == 0:
        
            # Popup if download took more than 2 minutes
            if (timeit.default_timer() - self.t) > 200:
                self.PopUp()

        #---# Soft Reset
            self.Loading.setHidden(True)
            
            self.locationbtn.setEnabled(True)
        
        self.ErrorOccured = False


    def InitiateThread(self, dat):
        for v in dat:
            worker = Worker(self.Download, v)
            worker.signals.finished.connect(self.thread_complete)
            
            self.threadpool.start(worker)

            print("Started a download!")


    def callback(self):
        # Timer
        if self.threads == 0:
            self.t = timeit.default_timer()

        # Link
        Link = clipboard.paste()

        # Pick either playlist mode or single mode
        Data = None

        try:
            Data = Playlist(Link).videos
            print(len(Data))
            print(Data[0].title)
        except:
            Data = [YouTube(Link)]
            print(len(Data))
            print(Data[0].title)

        # Increase Threads
        self.threads += len(Data)

        # Thread
        worker = Worker(self.InitiateThread, Data)
        self.threadpool.start(worker)

        # Uid
        self.DCount.setText(str(self.threads))
        self.Loading.setHidden(False)
        self.locationbtn.setEnabled(False)


    def RequestLocation(self):
        DownloadLocation = QFileDialog.getExistingDirectory(self, "Select Directory", Download)
    

    # method for creating widgets
    def initUI(self):
        # Window Setup
        self.setFixedSize(400, 0)
        self.center()
        self.setWindowTitle("Youtube Downloader")

        # Download Counter
        self.DCount = QLabel("0")
        self.DCount.adjustSize()

        # Download Button
        self.downloadbtn = QPushButton('Download', self)
        self.downloadbtn.setToolTip("Download Copied Link")
     
        self.downloadbtn.clicked.connect(self.callback)

        # Download Location Button
        self.locationbtn = QPushButton('..', self)
        self.locationbtn.clicked.connect(self.RequestLocation)

        # Loading Symbol
        self.Loading = QLabel()
        self.gif = QMovie("Loading.gif")
        self.gif.setScaledSize(QSize().scaled(20, 20, Qt.KeepAspectRatio))
        self.Loading.setMovie(self.gif)
        self.gif.start()
            
        # Layout
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        # Finish
        self.show()
        self.Loading.setHidden(True)


    def Download(self, dat): 
        # Get Name       
        try:
            self.SongName = dat.title
        except:
            self.ErrorOccured = True
            print("Invalid Link")

        # General
        SongName = self.SongName # Download Name for file
        SongDirectory = DownloadLocation + '\\' # Location of Download
        extension = ".mp3"

        if not os.path.isfile(SongDirectory + SongName + extension):
            # Generate Unique temp Name
            unique = str(uuid.uuid4().hex)

            while glob.glob(SongDirectory + unique + ".*"):
                unique = str(uuid.uuid4().hex)
            
            # Download Video
            vids = dat.streams.first()
            vids.download(SongDirectory, unique) 
            
            # Convert Video
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call([
                'ffmpeg',
                '-nostdin',
                '-i', os.path.join(SongDirectory, unique), os.path.join(SongDirectory, SongName + extension)], creationflags=CREATE_NO_WINDOW)

            # Delete Temp
            while os.path.isfile(SongDirectory + unique):
                if os.path.isfile(SongDirectory + SongName + extension):
                    os.remove(SongDirectory + unique)
        else:
            print("File Already Exists!")
        

# Main
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
  
    # create the instance of our Window
    window = Window()

    # Name Window
    window.setWindowTitle("Youtube Downloader")
  
    # start the app
    sys.exit(App.exec_())

    