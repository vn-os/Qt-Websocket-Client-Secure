import os, json
from enum import Enum

import websocket, ssl
from websocket import ABNF

from PyQt5 import uic as UiLoader
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from about import AboutDlg
from picker import Picker
from thread import StoppableThread
from utils import hexdump

DEFAULT_TIMEOUT = 30
PREFS_FILE_NAME = "prefs.json"

class color_t(str, Enum):
	success = "green"
	normal = "black"
	warn = "orange"
	error = "red"

class Window(QMainWindow):

	m_prefs = {}

	m_ws = None
	m_ws_codes = {}
	m_endpoint = ""
	m_sslfile = ""
	m_message = ""
	m_timeout = DEFAULT_TIMEOUT

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
		self.txt_timeout.textChanged.connect(self.on_changed_timeout)
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
		self.list_log.scrollToBottom()

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
			if os.path.exists(PREFS_FILE_NAME):
				with open(PREFS_FILE_NAME, "r+") as f:
					self.m_prefs = json.loads(f.read())
					self.m_timeout = self.prefs_get("timeout", DEFAULT_TIMEOUT)
					self.m_endpoint = self.prefs_get("endpoint").strip()
					self.m_sslfile = self.prefs_get("sslfile").strip()
					self.m_message = self.prefs_get("default_message")
					self.m_ws_codes = self.prefs_get("websocket_codes", {})
		except: self.status("Loading preferences file failed", color_t.error)
		self.update_ui(True)

	def prefs_save_to_file(self):
		self.prefs_set("endpoint", self.m_endpoint)
		self.prefs_set("timeout", self.m_timeout)
		self.prefs_set("sslfile", self.m_sslfile)
		self.prefs_set("default_message", self.m_message)
		with open(PREFS_FILE_NAME, "w+") as f:
			f.write(json.dumps(self.m_prefs, indent=4))

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
	
	def spotcheck_params(self):
		return self.m_timeout > 0 and self.m_endpoint.startswith(("ws:", "wss:"))

	def on_triggered_menu_help_about(self):
		AboutDlg(self.app).exec_()

	def on_triggered_menu_file_save(self):
		self.prefs_save_to_file()

	def on_triggered_menu_file_exit(self):
		self.ws_close()
		return self.close()

	def closeEvent(self, event):
		self.ws_close()
		event.accept()

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

	# Websocket Connection Setup

	m_ws_threads = {}

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

	def ws_on_data(self, ws, data, type, continuous):
		print("ws_on_data", ABNF.OPCODE_MAP.get(type), continuous)
		if type == ABNF.OPCODE_TEXT:
			self.log(data, color_t.error)
		elif type == ABNF.OPCODE_BINARY:
			self.log(hexdump(data), color_t.error)

	def ws_on_error(self, ws, error):
		self.m_ws = None
		self.status(str(error), color_t.error)
		self.update_ui()
		if error: raise error

	def ws_ready(self):
		return not self.m_ws is None

	def ws_start(self, use_ssl):
		# websocket.enableTrace(True)
		websocket.setdefaulttimeout(self.m_timeout)

		self.status("Connecting to server ...", color_t.warn)

		ws = websocket.WebSocketApp(
			self.m_endpoint,
			on_open=self.ws_on_open,
			on_close=self.ws_on_close,
			on_data=self.ws_on_data,
			on_error=self.ws_on_error,
			header={"test": "test"}
		)

		ssl_context = None
		if use_ssl: # websocket secure
			ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
			ssl_context.load_verify_locations(self.m_sslfile)

		def run(*args):
			try:
				ws.run_forever(sslopt={"context": ssl_context})
			except Exception as e:
				ws.close()
				if self.m_ws_threads[ws]: self.m_ws_threads[ws].stop()

		self.m_ws_threads[ws] = StoppableThread(target=run)
		self.m_ws_threads[ws].start()

	def ws_close(self):
		if self.ws_ready():
			self.status("Closing connection ...", color_t.warn)
			self.m_ws.close()
		self.status("Closed")

	def ws_send(self, data):
		if self.ws_ready(): self.m_ws.send(data)