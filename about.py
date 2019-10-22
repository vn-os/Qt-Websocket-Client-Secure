from PyQt5 import uic as UiLoader
from PyQt5.QtWidgets import QDialog

from defs import DIR

class AboutDlg(QDialog):
	def __init__(self):
		super(AboutDlg, self).__init__()

		self.initialize()

		return

	def initialize(self):
		UiLoader.loadUi(RF"{DIR}\res\about.ui", self)

		self.buttonBox.accepted.connect(self.on_accepted)
		self.buttonBox.rejected.connect(self.on_rejected)

		self.variable = "Close"

		return

	def on_accepted(self):
		self.variable = "Ok"

	def on_rejected(self):
		self.variable = "Cancel"