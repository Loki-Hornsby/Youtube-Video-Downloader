# ----- Compile Command ----- #
# pyinstaller -w --onefile DownloadApp.pyw

from __future__ import print_function, unicode_literals
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pytube import YouTube
from pytube.helpers import safe_filename
from tube_dl import Youtube

from sys import argv
import sys
from subprocess import call
import subprocess

import os
from winreg import *
from pathlib import Path
import glob
import contextlib
import traceback

import ffmpeg

import clipboard
import time

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

        self.LogBuildLine = ""
        self.ErrorOccured = False

        self.initUI()

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
        
        # |0,0|0,1|0,2|0,3|
        # |1,0|1,1|1,2|1,3|
        # |2,0|2,1|2,2|2,3|
        # |3,0|3,1|3,2|3,3|

        layout.addWidget(self.DCount,       0,0)
        layout.addWidget(self.downloadbtn,  0,1)
        layout.addWidget(self.Loading,      0,2)
        
        self.horizontalGroupBox.setLayout(layout)

    def thread_complete(self):
        self.threads -= 1

        self.DCount.setText(str(self.threads))

        self.Loading.setHidden(True)
        
        self.ErrorOccured = False
        
    def callback(self):
        worker = Worker(self.Download)
        worker.signals.finished.connect(self.thread_complete)
        
        self.threadpool.start(worker)

        self.threads += 1
        self.DCount.setText(str(self.threads))
        self.Loading.setHidden(False)
        
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

    def Download(self, progress_callback):        
        Link = clipboard.paste()
        
        try:
            SongName = YouTube(Link).title
        except:
            self.ErrorOccured = True
            #self.logTextBox.appendPlainText("Invalid Link")

        vnum = 1

        yt = YouTube(Link)
        vids = yt.streams.filter(only_audio=True)

        DownloadName = vids[vnum].default_filename
        Downloadfilename, Downloadfile_extension = os.path.splitext(DownloadName)
        parent_dir = Downloads + '\\'
        extension = ".mp3"
        allfileid = ".*"
        temp_name = Downloadfilename
        temp_path = parent_dir + Downloadfilename
        
        # Temp File Check
        counter = 1

        while glob.glob(temp_path + allfileid):
            counter += 1
            temp_name = Downloadfilename + str(counter)
            temp_path = parent_dir + Downloadfilename + str(counter)
    
        # Download And Convert
        vids[vnum].download(parent_dir, temp_name)
        
        # Convert
        try:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call([
                'ffmpeg',
                '-nostdin',
                '-i', os.path.join(parent_dir, temp_name + Downloadfile_extension), os.path.join(parent_dir, temp_name + extension)], creationflags=CREATE_NO_WINDOW)

            # Delete Temp File
            if os.path.isfile(parent_dir + temp_name + Downloadfile_extension):
                os.remove(parent_dir + temp_name + Downloadfile_extension)
        except:
            self.ErrorOccured = True
            #self.logTextBox.appendPlainText(Link + " Failed")
        
# Main
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
  
    # create the instance of our Window
    window = Window()
  
    # start the app
    sys.exit(App.exec_())

    
