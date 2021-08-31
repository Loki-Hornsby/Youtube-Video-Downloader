# ----- Compile Command ----- #
""" 

pyinstaller -w --onefile DownloadApp.pyw

"""

# ----- Modules ----- #

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

import logging


# ----- Log Setup ----- #

class LoggerWriter:
    def __init__(self, level):
        # self.level is really like using log.debug(message)
        # at least in my case
        self.level = level

    def write(self, message):
        # if statement reduces the amount of newlines that are
        # printed to the logger
        if message != '\n':
            self.level(message)

    def flush(self):
        # create a flush method so things can be flushed when
        # the system wants to. Not sure if simply 'printing'
        # sys.stderr is the correct way to do it, but it seemed
        # to work properly for me.
        self.level(sys.stderr)

# Path
p = "output log/LOG.txt"

# Configure file
logging.basicConfig(
    filename = p,
    format='%(message)s',
    level=logging.INFO)

# Clear file of any previous text
with open(p, 'w'):
    pass

# Get/Create logger
logger = logging.getLogger(__name__)

# Redirect errors to output log
sys.stdout = LoggerWriter(logger.info)
sys.stderr = LoggerWriter(logger.warning)

# Output wether running from bundle or python process
_runmode = ""

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    _runmode = "running in a PyInstaller bundle"
else:
    _runmode = "running in a normal Python process"

# Output number of threads
th = QThreadPool()
_threads = str(th.maxThreadCount())

# Selected extension
extension = ".mp3"

# Output spec info
import platform
_system = platform.system() 
_machine = platform.machine() 
_platform = platform.platform() 
_ver = platform.version()

# Python info
_Py_ver = str(sys.version.split(', '))
_modu = ("\n" + "".ljust(8)).join(sys.modules.keys())

# build number
build_number = str(1)
logger.info("Build Number: " + build_number)

# Build Output
logger.info("\n> \YOUTUBE DOWNLOADER/ <\n")
logger.info("Debug Info:")

logger.info(
        "".ljust(4) + "Run Mode:".ljust(17)         + "".ljust(4)    + _runmode  +  "\n"  +
        "".ljust(4) + "Threads:".ljust(17)          + "".ljust(4)    + _threads  +  "\n"  +
        "".ljust(4) + "Download Ext:".ljust(17)     + "".ljust(4)    + extension +  "\n"  +
        "".ljust(4) +                                                               "\n"  +
        "".ljust(4) + "System:".ljust(17)           + "".ljust(4)    + _system   +  "\n"  +
        "".ljust(4) + "Machine:".ljust(17)          + "".ljust(4)    + _machine  +  "\n"  +
        "".ljust(4) + "Platform:".ljust(17)         + "".ljust(4)    + _platform +  "\n"  +
        "".ljust(4) + "Version:".ljust(17)          + "".ljust(4)    + _ver      +  "\n"  +
        "".ljust(4) +                                                               "\n"  +
        "".ljust(4) + "Python version:".ljust(17)   + "".ljust(4)    + _Py_ver   +  "\n"  +
        "".ljust(4) + "Modules:".ljust(17)          + "\n".ljust(9)  + _modu     +  "\n"  
        )

# ----- Threading ----- #

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


# ----- Notification Label ----- #

class AnimationLabel(QLabel):
    # Initialize Label
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.animation = QVariantAnimation()
        self.animation.valueChanged.connect(self.changeColor)
    
    # Change labels text
    def changetext(self, s):
        self.setText(s)

    # Animations
    @pyqtSlot(QVariant)

    # Change label color
    def changeColor(self, color):
        palette = self.palette()
        palette.setColor(QPalette.WindowText, color)
        self.setPalette(palette)

    # fade in label
    def startFadeIn(self, startC, endC):
        self.animation.stop()
        self.animation.setStartValue(startC)
        self.animation.setEndValue(endC)
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.InBack)
        self.animation.start()

    # fade out label
    def startFadeOut(self, startC, endC):
        self.animation.stop()
        self.animation.setStartValue(startC)
        self.animation.setEndValue(endC)
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.InBack)
        self.animation.start()

    # disable ui objects
    def disableUi(self, a, b):
        a.setEnabled(False)
        b.setEnabled(False)

    # enable ui objects
    def enableUi(self, a, b):
        a.setEnabled(True)
        b.setEnabled(True)

    # begin preset animation
    def BeginAnimation(self, a, b, s, startC, endC):
        self.changetext(s)

        self.disableUi(a, b)

        self.startFadeIn(startC, endC)
        self.setHidden(False)

        QTimer.singleShot(1000, lambda: self.startFadeOut(endC, startC))
        QTimer.singleShot(2000, lambda: self.startFadeIn(startC, endC))
        QTimer.singleShot(3000, lambda: self.startFadeOut(endC, startC))
        
        QTimer.singleShot(4000, lambda: self.setHidden(True))
        QTimer.singleShot(4000, lambda: self.enableUi(a, b))


# ----- Main App ----- #

class Window(QWidget):

    # Initialize app
    def __init__(self):
        super(Window, self).__init__()

        # Default download location
        self.DownloadLocation = "downloads"

        # Setup Threads
        self.threads = 0
        self.threadpool = QThreadPool()

        # Initialize Ui
        self.initUI()

        # Finish initialization
        logger.info("> Initialization done")
    

    # Center window
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    # Create Grid
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

        layout.addWidget(self.flashlbl,         1,1)
        
        self.horizontalGroupBox.setLayout(layout)

    def showAnimation(self, ind):
        if ind == 1:
            logger.info("[-] copied link was invalid or inaccessible")

            self.flashlbl.BeginAnimation(
                self.downloadbtn, 
                self.locationbtn, 
                "Error! The copied link is either invalid or inaccessible",
                QColor(255, 0, 0, 0),
                QColor(100, 0, 0, 255))

        elif ind == 2:
            self.flashlbl.BeginAnimation(
                self.downloadbtn, 
                self.locationbtn, 
                "Completed all downloads!",
                QColor(0, 255, 0, 0),
                QColor(0, 100, 0, 255))


    # On Thread Completed
    def thread_complete(self):
        # Threads
        self.threads -= 1
        self.DCount.setText(str(self.threads))

        # No Threads Left Condition
        if self.threads == 0:
            self.showAnimation(2)
            
            # Soft Reset
            self.Loading.setHidden(True)
            self.locationbtn.setEnabled(True)

    # Empty thread
    def blank(self):
        pass

    # Begin Thread(s)
    def InitiateThread(self, dat):
        for v in dat:
            if not os.path.isfile(self.DownloadLocation + '\\' + v.title + extension):
                worker = Worker(self.Download, v)
                worker.signals.finished.connect(self.thread_complete)
                
                self.threadpool.start(worker)
            else: 
                worker = Worker(self.blank)
                worker.signals.finished.connect(self.thread_complete)

                self.threadpool.start(worker)

                logger.info("[%] " + v.title + "\n    File Already Exists!")

    # On download button pressed
    def callback(self):
        # Timer
        if self.threads == 0:
            self.t = timeit.default_timer()

        # Link
        Link = clipboard.paste()

        # Pick either playlist mode or single mode or catch an error
        Data = None

        # Multi
        if Data == None:
            try:
                Data = Playlist(Link).videos
                len(Data)
                Data[0].title
            except:
                Data = None

        # Single
        if Data == None:
            try:
                Data = [YouTube(Link)]
                len(Data)
                Data[0].title
            except:
                Data = None

        # If Data is a valid value
        if Data != None:
            # Increase Threads
            self.threads += len(Data)

            # Thread
            worker = Worker(self.InitiateThread, Data)
            self.threadpool.start(worker)

            # Uid
            self.DCount.setText(str(self.threads))
            self.Loading.setHidden(False)
            self.locationbtn.setEnabled(False)
        else:
            self.showAnimation(1)
    

    # Request folder location
    def RequestLocation(self):
        self.DownloadLocation = QFileDialog.getExistingDirectory(self, "Select Directory")
    

    # Initialize UI Objects
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
        self.downloadbtn.setToolTip("Download copied link")
     
        self.downloadbtn.clicked.connect(self.callback)

        # Download Location Button
        self.locationbtn = QPushButton('..', self)
        self.locationbtn.setToolTip("Change download location")

        self.locationbtn.clicked.connect(self.RequestLocation)

        # Loading Symbol
        self.Loading = QLabel()
        self.gif = QMovie("assets/Loading.gif")
        self.gif.setScaledSize(QSize().scaled(20, 20, Qt.KeepAspectRatio))
        self.Loading.setMovie(self.gif)
        self.gif.start()

        # Error Ouput Label
        self.flashlbl = AnimationLabel("Something has messed up if your seeing this")
            
        # Layout
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        # Show and hide ui
        self.show()
        self.Loading.setHidden(True)
        self.flashlbl.setHidden(True)

        logger.info("> Initializating Gui...")


    # Download a video
    def Download(self, dat): 
        # General
        VideoName = dat.title # Download Name for file
        VideoDirectory = self.DownloadLocation + '\\' # Location of Download
        
        logger.info("[+] " + VideoName + "\n    Added to download list")

        # Generate Unique temp Name
        unique = str(uuid.uuid4().hex)

        while glob.glob(VideoDirectory + unique + ".*"):
            unique = str(uuid.uuid4().hex)

        # Download Video
        vids = dat.streams.first()
        vids.download(VideoDirectory, unique) 
        
        # Convert Video
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call([
            'FFmpeg/bin/ffmpeg.exe',                                # Using ffmpeg - i call the exe directly.
            '-nostdin',                                             # Disable interaction
            '-i',                                                   #| Input -->
            os.path.join(VideoDirectory, unique),                   #|| Input
            os.path.join(VideoDirectory, VideoName + extension)],   #|| Ouput
            creationflags=CREATE_NO_WINDOW)                         # Disable console window from appearing
            
        # Delete Temp
        logger.info("[*] " + VideoName + "\n    Finishing up")

        while os.path.isfile(VideoDirectory + unique):
            if os.path.isfile(VideoDirectory + VideoName + extension):
                os.remove(VideoDirectory + unique)


# ----- Run App ----- #
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
  
    # create the instance of our Window
    window = Window()

    # Name Window
    window.setWindowTitle("Youtube Downloader")
  
    # Start the app
    logger.info("> App Starting! \n")

    sys.exit(App.exec_())
