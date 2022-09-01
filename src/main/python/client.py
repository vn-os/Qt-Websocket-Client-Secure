import os, json
from enum import Enum

import websocket, ssl
from websocket import ABNF

from hexdump import hexdump # from utils import hexdump
from thread import StoppableThread

DEFAULT_TIMEOUT = 30
PREFS_FILE_NAME = "prefs.json"

class color_t(str, Enum):
	# status
	success = "green"
	normal = "black"
	warn = "orange"
	error = "red"
	# color
	red = "red"
	green = "green"

class WSClient:
	""" Websocket Client """

	m_prefs = {}

	m_ws = None
	m_ws_codes = {}
	m_endpoint = ""
	m_sslfile = ""
	m_message = ""
	m_timeout = DEFAULT_TIMEOUT

	m_ws_threads = {}

	def __init__(self, *args, **kwargs):
		pass

	def update_ui(self, update_values=False):
		assert False, "missing implementation"

	def log(self, text, color=color_t.normal):
		assert False, "missing implementation"

	def status(self, text, color=color_t.normal):
		assert False, "missing implementation"

	def prefs_get(self, name, default=""):
		return self.m_prefs[name] if name in self.m_prefs.keys() else default

	def prefs_set(self, name, value):
		self.m_prefs[name] = value

	def prefs_load_from_file(self):
		try:
			if os.path.exists(PREFS_FILE_NAME):
				with open(PREFS_FILE_NAME, "r+") as f:
					self.m_prefs = json.loads(f.read())
					self.m_timeout = self.prefs_get("timeout", DEFAULT_TIMEOUT)
					self.m_endpoint = self.prefs_get("endpoint").strip()
					self.m_sslfile = self.prefs_get("sslfile").strip()
					self.m_message = self.prefs_get("default_message")
					self.m_ws_codes = self.prefs_get("websocket_codes", {})
		except:
			self.status("Loading preferences file failed", color_t.error)
		self.update_ui(True)

	def prefs_save_to_file(self):
		self.prefs_set("endpoint", self.m_endpoint)
		self.prefs_set("timeout", self.m_timeout)
		self.prefs_set("sslfile", self.m_sslfile)
		self.prefs_set("default_message", self.m_message)
		with open(PREFS_FILE_NAME, "w+") as f:
			f.write(json.dumps(self.m_prefs, indent=4))

	def spotcheck_params(self):
		return self.m_timeout > 0 and self.m_endpoint.startswith(("ws:", "wss:"))

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

	def ws_on_error(self, ws, error):
		self.m_ws = None
		self.status(str(error), color_t.error)
		self.update_ui()
		if error: raise error

	def ws_on_data(self, ws, data, type, continuous):
		if type == ABNF.OPCODE_TEXT:
			self.log(data, color_t.red)
		elif type == ABNF.OPCODE_BINARY:
			dump = hexdump(data)
			self.log(str(dump), color_t.red)
		else:
			print("received data type did not support", ABNF.OPCODE_MAP.get(type))

	def ws_send(self, data):
		if self.ws_ready(): self.m_ws.send(data)

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
