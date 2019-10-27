from PyQt5.QtWidgets import QFileDialog

DEF_DIR = ""
DEF_FILTER = "All Files (*.*)"

class DFDialog:

	@staticmethod
	def select_file(parent = None, defaultStype = True):
		options = QFileDialog.Options()
		if not defaultStype: options |= QFileDialog.DontUseNativeDialog
		return QFileDialog.getOpenFileName(
			parent, "Select File", DEF_DIR, DEF_FILTER, options=options)[0]

	@staticmethod
	def select_files(parent=None, defaultStype=True):
		options = QFileDialog.Options()
		if not defaultStype: options |= QFileDialog.DontUseNativeDialog
		return QFileDialog.getOpenFileNames(
			parent, "Select Files", DEF_DIR, DEF_FILTER, options=options)[0]

	@staticmethod
	def save_file(parent=None, defaultStype=True):
		options = QFileDialog.Options()
		if not defaultStype: options |= QFileDialog.DontUseNativeDialog
		return QFileDialog.getSaveFileName(
			parent, "Select File", DEF_DIR, DEF_FILTER, options=options)[0]

	@staticmethod
	def select_directory(parent=None, defaultStype=True):
		options = QFileDialog.Options()
		if not defaultStype: options |= QFileDialog.DontUseNativeDialog
		options |= QFileDialog.ShowDirsOnly
		return QFileDialog.getExistingDirectory(
			parent, "Select Directory", DEF_DIR, options=options)
