from PyQt5 import uic as UiLoader
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from defs import DIR
from about import AboutDlg
from dfdialog import DFDialog

class Window(QMainWindow):
	def __init__(self, app):
		super(Window, self).__init__()
		self.app = app
		self.setup_ui()
		return

	def setup_ui(self):

		# Load UI from file
		UiLoader.loadUi(self.app.get_resource("main.ui"), self)

		# Signal & Slot
		self.actionExit.triggered.connect(self.on_triggered_menu_file_exit)
		self.actionAbout.triggered.connect(self.on_triggered_menu_help_about)
		self.btn_connect.clicked.connect(self.on_clicked_button_connect)
		self.btn_send_message.clicked.connect(self.on_clicked_button_send_message)
		self.btn_clear_list_log.clicked.connect(self.on_clicked_button_clear_list_log)

		return

	def is_default_style(self):
		return QApplication.instance().style().metaObject().className() == "QWindowsVistaStyle"

	def on_triggered_menu_help_about(self):
		self.about_dialog = AboutDlg(self.app)
		response = self.about_dialog.exec_()
		print(f"{self.about_dialog.__class__.__name__} {self.about_dialog.variable} {response}")
		return

	def on_triggered_menu_file_exit(self):
		return self.close()

	def on_clicked_button_connect(self):
		endpoint = self.txt_endpoint.text()
		print("on_clicked_button_connect", endpoint)
		# your code here
		return

	def on_clicked_button_send_message(self):
		message = self.txt_message.toPlainText()
		self.list_log.addItem(QListWidgetItem(message))
		print("on_clicked_button_send_message", message)
		# your code here
		return

	def on_clicked_button_clear_list_log(self):
		self.list_log.clear()
		return
