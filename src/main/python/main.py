import os, json
from enum import Enum

from PyQt5 import uic as UiLoader
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from about import AboutDlg
from picker import Picker

import websocket, ssl
from _thread import start_new_thread

class color_t(str, Enum):
	success = "green"
	normal = "black"
	warn = "orange"
	error = "red"

class Window(QMainWindow):

	m_prefs = {}
	m_prefs_file_name = "prefs.json"

	m_ws = None
	m_ws_codes = {}
	m_endpoint = ""
	m_message_text = ""
	m_ssl_file_path = ""

	def __init__(self, app):
		super(Window, self).__init__()
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
		self.btn_connect.clicked.connect(self.on_clicked_button_connect)
		self.btn_browse_ssl_file.clicked.connect(self.on_clicked_button_browse_ssl_file)
		self.txt_message.textChanged.connect(self.on_changed_message)
		self.btn_send_message.clicked.connect(self.on_clicked_button_send_message)
		self.btn_clear_list_log.clicked.connect(self.on_clicked_button_clear_list_log)
		# load and apply prefs
		self.prefs_load_and_apply()

	def is_default_style(self):
		return QApplication.instance().style().metaObject().className() == "QWindowsVistaStyle"

	def log(self, text, color=color_t.normal):
		item = QListWidgetItem(text)
		item.setForeground(QColor(color))
		self.list_log.addItem(item)

	def status(self, text, color=color_t.normal):
		self.lbl_status.setText(text)
		self.lbl_status.setToolTip(text)
		palette = self.lbl_status.palette()
		palette.setColor(QPalette.WindowText, QColor(color))
		self.lbl_status.setPalette(palette)

	def prefs_get(self, name, default=""):
		return self.m_prefs[name] if name in self.m_prefs.keys() else default

	def prefs_set(self, name, value):
		self.m_prefs[name] = value

	def prefs_load_and_apply(self):
		try:
			with open(self.m_prefs_file_name, "r+") as f:
				self.m_prefs = json.loads(f.read())
				self.m_endpoint = self.prefs_get("endpoint").strip()
				self.m_ssl_file_path = self.prefs_get("ssl_file_path").strip()
				self.m_message_text = self.prefs_get("default_message")
				self.m_ws_codes = self.prefs_get("websocket_codes", {})
		except: print("prefs not found or loading failed")
		self.update_ui(True)

	def prefs_save_to_file(self):
		self.prefs_set("endpoint", self.m_endpoint)
		self.prefs_set("ssl_file_path", self.m_ssl_file_path)
		self.prefs_set("default_message", self.m_message_text)
		with open(self.m_prefs_file_name, "w+") as f:
			f.write(json.dumps(self.m_prefs, indent=4))

	def update_ui(self, init=False):
		# enabled/disabled state
		self.txt_endpoint.setEnabled(not self.ws_ready())
		self.txt_ssl_file_path.setEnabled(not self.ws_ready())
		self.btn_browse_ssl_file.setEnabled(not self.ws_ready())
		self.txt_message.setEnabled(self.ws_ready())
		self.btn_send_message.setEnabled(self.ws_ready())
		# edit-box endpoint
		self.txt_endpoint.setText(self.m_endpoint)
		# edit-box ssl file path
		self.txt_ssl_file_path.setText(os.path.basename(self.m_ssl_file_path))
		self.txt_ssl_file_path.setToolTip(self.m_ssl_file_path)
		self.btn_connect.setText("CONNECT" if self.m_ws is None else "DISCONNECT")
		# the first time when launching
		if init: self.txt_message.insertPlainText(self.m_message_text) # edit-box message

	def on_triggered_menu_help_about(self):
		AboutDlg(self.app).exec_()

	def on_triggered_menu_file_save(self):
		self.prefs_save_to_file()

	def on_triggered_menu_file_exit(self):
		self.ws_close()
		return self.close()

	def on_changed_endpoint(self):
		self.m_endpoint = self.txt_endpoint.text().strip()
		self.btn_connect.setEnabled(self.m_endpoint.startswith(("ws:", "wss:")))

	def on_clicked_button_connect(self):
		self.ws_start() if self.m_ws is None else self.ws_close()

	def on_clicked_button_browse_ssl_file(self):
		self.m_ssl_file_path = Picker.select_file(self, self.is_default_style())
		self.update_ui()

	def on_changed_message(self):
		self.m_message_text = self.txt_message.toPlainText()

	def on_clicked_button_send_message(self):
		self.log(self.m_message_text, color_t.success)
		print("on_clicked_button_send_message", self.m_message_text)
		self.ws_send(self.m_message_text)

	def on_clicked_button_clear_list_log(self):
		self.list_log.clear()

	# Websocket Connection Setup

	def ws_on_open(self, ws):
		self.m_ws = ws
		self.status("Opened", color_t.success)
		self.update_ui()

	def ws_on_close(self, ws, close_status_code, close_msg):
		text = "Closed"
		color = color_t.normal
		if close_msg:
			text = close_msg
			color = color_t.error
		elif close_status_code:
			msg = None
			ws_close_codes = self.m_ws_codes.get("close")
			if ws_close_codes: msg = ws_close_codes.get(str(close_status_code))
			text = f"Close code {close_status_code}" if msg is None else msg
			color = color_t.error
		if self.ws_ready(): self.status(text, color)
		self.m_ws = None
		self.update_ui()

	def ws_on_message(self, ws, message):
		self.log(message, color_t.error)

	def ws_on_error(self, ws, error):
		self.status(str(error), color_t.error)

	def ws_ready(self):
		return not self.m_ws is None

	def ws_start(self):
		# websocket.enableTrace(True)
		# websocket.setdefaulttimeout(5)

		self.status("Connecting to server ...", color_t.warn)

		ws = websocket.WebSocketApp(
			self.m_endpoint,
			on_open=self.ws_on_open,
			on_close=self.ws_on_close,
			on_message=self.ws_on_message,
			on_error=self.ws_on_error,
			header={"test": "test"}
		)

		ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
		ssl_context.load_verify_locations(self.m_ssl_file_path)

		def run(*args): ws.run_forever(sslopt={"context": ssl_context})
		start_new_thread(run, ())

	def ws_close(self):
		if self.ws_ready(): self.m_ws.close()

	def ws_send(self, data):
		if self.ws_ready(): self.m_ws.send(data)