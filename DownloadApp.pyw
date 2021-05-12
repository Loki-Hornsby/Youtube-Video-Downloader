# ----- Compile Command ----- #
# pyinstaller -w --onefile DownloadApp.pyw

from __future__ import print_function, unicode_literals
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import sys
from sys import argv  
from subprocess import call
import subprocess
import traceback
from pathlib import Path
import glob
import contextlib
from pytube import YouTube
from pytube.helpers import safe_filename
from tube_dl import Youtube
import ffmpeg
import sys
import os
from winreg import *

# Download
with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
    Downloads = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

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

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

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
        
        layout.addWidget(self.Entry,   0,0)
        layout.addWidget(self.pbar,    1,0)
        layout.addWidget(self.btn,     1,1)
        layout.addWidget(self.Loading, 0,1)
            
        self.horizontalGroupBox.setLayout(layout)

    def GetSongName(self, progress_callback):
        try:
            self.SongName = YouTube(self.Link).title
            self.Download()
        except Exception as e:
            print(e)
            print("Incorrect Name :)")

    def thread_complete(self):
        self.Loading.setHidden(True)
        self.Entry.setEnabled(True)
        self.Entry.clear()
        self.pbar.resetFormat()
    
    def callback(self):
        self.Link = self.Entry.text()
    
        if len(self.Link) > 0:
            worker = Worker(self.GetSongName)
            worker.signals.finished.connect(self.thread_complete)
    
            self.threadpool.start(worker)

            self.Entry.setEnabled(False)
            self.Loading.setHidden(False)

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

        print("Ui Setup!")

    def percent(self, tem, total):
        perc = (float(tem) / float(total)) * float(100)
        return perc
    
    def DownloadHook(self, stream, chunk, bytes_remaining):
        self.pbar.setValue(self.percent(bytes_remaining, 1))
            
    def Download(self):
        # https://www.youtube.com/watch?v=9nY9eUvAq5U - short
        # https://www.youtube.com/watch?v=kxGWsHYITAw - long

        # https://www.youtube.com/watch?v=szHSZf8zkyA
        # https://www.youtube.com/watch?v=NvcasLaeB_s
        # https://www.youtube.com/watch?v=ocD0ZIjp_9c

        vnum = 1

        yt = YouTube(self.Link, on_progress_callback = self.DownloadHook)
        vids = yt.streams.filter(only_audio=True).all()

        DownloadName = vids[vnum].default_filename
        Downloadfilename, Downloadfile_extension = os.path.splitext(DownloadName)
        parent_dir = Downloads + '\\'
        extension = ".mp3"
        allfileid = ".*"
        temp_name = ""
        temp_path = parent_dir + Downloadfilename
        
        # Temp File Check
        counter = 1

        while glob.glob(temp_path + allfileid):
            counter += 1
            temp_name = Downloadfilename + str(counter)
            temp_path = parent_dir + Downloadfilename + str(counter)
    
        # Download
        vids[vnum].download(parent_dir, temp_name)

        # Convert
        try:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call([
                'ffmpeg',
                '-loglevel', 'error',
                '-i', os.path.join(parent_dir, temp_name + Downloadfile_extension), os.path.join(parent_dir, temp_name + extension)], creationflags=CREATE_NO_WINDOW)
        except:
            print("Error Raised?")

        # Delete Temp File
        os.remove(parent_dir + temp_name + Downloadfile_extension)

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

    
