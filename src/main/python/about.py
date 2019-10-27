from PyQt5 import uic as UiLoader
from PyQt5.QtWidgets import QDialog

from defs import DIR

class AboutDlg(QDialog):
	def __init__(self, app):
		super(AboutDlg, self).__init__()
		self.app = app
		self.setup_ui()
		return

	def setup_ui(self):
	
		# Load UI from file
		UiLoader.loadUi(self.app.get_resource("about.ui"), self)

		# Controls
		self.buttonBox.accepted.connect(self.on_accepted)
		self.buttonBox.rejected.connect(self.on_rejected)

		# Others
		self.variable = "Close"

		return

	def on_accepted(self):
		self.variable = "Ok"

	def on_rejected(self):
		self.variable = "Cancel"