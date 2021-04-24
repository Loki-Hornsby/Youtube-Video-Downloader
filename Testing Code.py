# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import time

class Example(QWidget):

	def __init__(self):
		super().__init__()

		# calling initUI method
		self.initUI()

	# method for creating widgets
	def initUI(self):

		# creating progress bar
		self.pbar = QProgressBar(self)

		# setting its geometry
		self.pbar.setGeometry(30, 40, 200, 25)

		# creating push button
		self.btn = QPushButton('Start', self)

		# changing its position
		self.btn.move(40, 80)

		# adding action to push button
		self.btn.clicked.connect(self.doAction)

		# setting window geometry
		self.setGeometry(300, 300, 280, 170)

		# setting window action
		self.setWindowTitle("Python")

		# showing all the widgets
		self.show()

	# when button is pressed this method is being called
	def doAction(self):

		# setting for loop to set value of progress bar
		for i in range(101):

			# slowing down the loop
			time.sleep(0.05)

			# setting value to progress bar
			self.pbar.setValue(i)

# main method
if __name__ == '__main__':
	
	
	# create pyqt5 app
	App = QApplication(sys.argv)

	# create the instance of our Window
	window = Example()

	# start the app
	sys.exit(App.exec())
