import os

from PyQt5 import uic as UiLoader
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from defs import DIR
from about import AboutDlg
from picker import Picker

class Window(QMainWindow):

	m_endpoint = ""
	m_message_text = ""
	m_ssl_file_path = ""

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
		self.txt_endpoint.textChanged.connect(self.on_changed_endpoint)
		self.btn_connect.clicked.connect(self.on_clicked_button_connect)
		self.btn_browse_ssl_file.clicked.connect(self.on_clicked_button_browse_ssl_file)
		self.btn_send_message.clicked.connect(self.on_clicked_button_send_message)
		self.btn_clear_list_log.clicked.connect(self.on_clicked_button_clear_list_log)

		return

	def is_default_style(self):
		return QApplication.instance().style().metaObject().className() == "QWindowsVistaStyle"

	def log(self, text, color):
		item = QListWidgetItem(text)
		item.setForeground(QColor(color))
		self.list_log.addItem(item)

	def on_triggered_menu_help_about(self):
		self.about_dialog = AboutDlg(self.app)
		response = self.about_dialog.exec_()
		print(f"{self.about_dialog.__class__.__name__} {self.about_dialog.variable} {response}")
		return

	def on_triggered_menu_file_exit(self):
		return self.close()

	def on_changed_endpoint(self):
		endpoint = self.txt_endpoint.text()
		self.btn_connect.setEnabled(len(endpoint) > 0 and endpoint.startswith(("ws:", "wss:")))
		return

	def on_clicked_button_connect(self):
		self.m_endpoint = self.txt_endpoint.text()
		print("on_clicked_button_connect", self.m_endpoint)
		# your code here
		return

	def on_clicked_button_browse_ssl_file(self):
		self.m_ssl_file_path = Picker.select_file(self, self.is_default_style())
		self.txt_ssl_file_path.setText(os.path.basename(self.m_ssl_file_path))
		self.txt_ssl_file_path.setToolTip(self.m_ssl_file_path)
		print("on_clicked_button_browse_ssl_file", self.m_ssl_file_path)
		return

	def on_clicked_button_send_message(self):
		self.m_message_text = self.txt_message.toPlainText()
		self.log(self.m_message_text, "green")
		print("on_clicked_button_send_message", self.m_message_text)
		# your code here
		return

	def on_clicked_button_clear_list_log(self):
		self.list_log.clear()
		return
