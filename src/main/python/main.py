import os

from PyQt5 import uic as UiLoader
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from client import *
from about import AboutDlg
from picker import Picker

class Window(QMainWindow, WSClient):

	def __init__(self, app):
		super(Window, self).__init__()
		super(WSClient, self).__init__()
		self.app = app
		self.setup_ui()
		return

	def setup_ui(self):
		# load ui from file
		UiLoader.loadUi(self.app.get_resource("main.ui"), self)
		# signal & slot
		self.actionSave.triggered.connect(self.on_triggered_menu_file_save)
		self.actionExit.triggered.connect(self.on_triggered_menu_file_exit)
		self.actionAbout.triggered.connect(self.on_triggered_menu_help_about)
		self.txt_endpoint.textChanged.connect(self.on_changed_endpoint)
		self.txt_timeout.textChanged.connect(self.on_changed_timeout)
		self.btn_connect.clicked.connect(self.on_clicked_button_connect)
		self.btn_browse_ssl_file.clicked.connect(self.on_clicked_button_browse_ssl_file)
		self.txt_message.textChanged.connect(self.on_changed_message)
		self.btn_send_message.clicked.connect(self.on_clicked_button_send_message)
		self.btn_clear_list_log.clicked.connect(self.on_clicked_button_clear_list_log)
		# load  prefs from file
		self.prefs_load_from_file()

	def is_default_style(self):
		return QApplication.instance().style().metaObject().className() == "QWindowsVistaStyle"

	def closeEvent(self, event):
		self.ws_close()
		event.accept()

	def log(self, text, color=color_t.normal):
		item = QListWidgetItem(text)
		item.setForeground(QColor(color))
		self.list_log.addItem(item)
		self.list_log.scrollToBottom()

	def status(self, text, color=color_t.normal):
		self.lbl_status.setText(text)
		self.lbl_status.setToolTip(text)
		palette = self.lbl_status.palette()
		palette.setColor(QPalette.WindowText, QColor(color))
		self.lbl_status.setPalette(palette)

	def update_ui(self, update_values=False):
		self.txt_endpoint.setEnabled(not self.ws_ready())
		self.txt_timeout.setEnabled(not self.ws_ready())
		self.txt_ssl_file_path.setEnabled(not self.ws_ready())
		self.btn_browse_ssl_file.setEnabled(not self.ws_ready())
		self.txt_message.setEnabled(self.ws_ready())
		self.btn_send_message.setEnabled(self.ws_ready())
		if update_values:
			self.txt_endpoint.setText(str(self.m_endpoint))
			self.txt_ssl_file_path.setText(os.path.basename(self.m_sslfile))
			self.txt_ssl_file_path.setToolTip(self.m_sslfile)
			self.txt_timeout.setText(str(self.m_timeout))
			self.txt_message.insertPlainText(self.m_message)  # edit-box message
		self.btn_connect.setText("DISCONNECT" if self.ws_ready() else "CONNECT")
	
	def on_triggered_menu_help_about(self):
		AboutDlg(self.app).exec_()

	def on_triggered_menu_file_save(self):
		self.prefs_save_to_file()

	def on_triggered_menu_file_exit(self):
		self.ws_close()
		return self.close()

	def on_changed_endpoint(self):
		self.m_endpoint = self.txt_endpoint.text().strip()
		self.btn_connect.setEnabled(self.spotcheck_params())

	def on_changed_timeout(self):
		timeout = self.txt_timeout.text().strip()
		if not timeout.isdecimal():
				timeout = str(0)
		self.m_timeout = int(timeout)
		self.btn_connect.setEnabled(self.spotcheck_params())

	def on_clicked_button_connect(self):
		if not self.ws_ready():
			use_ssl = self.m_endpoint.startswith("wss:")
			if use_ssl and not os.path.exists(self.m_sslfile):
				self.status("This end-point required SSL file", color_t.error)
				return
			self.ws_start(use_ssl)
		else:
			self.ws_close()

	def on_clicked_button_browse_ssl_file(self):
		self.m_sslfile = Picker.select_file(self, self.is_default_style())
		self.update_ui(True)

	def on_changed_message(self):
		self.m_message = self.txt_message.toPlainText()

	def on_clicked_button_send_message(self):
		self.log(self.m_message, color_t.success)
		self.ws_send(self.m_message)

	def on_clicked_button_clear_list_log(self):
		self.list_log.clear()