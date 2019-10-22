from PyQt5 import uic as UiLoader
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem

from defs import DIR
from about import AboutDlg
from dfdialog import DFDialog

class Window(QMainWindow):
	def __init__(self):
		super(Window, self).__init__()

		self.setup_ui()

		return

	def setup_ui(self):

		# Load UI from file

		UiLoader.loadUi(RF"{DIR}\res\main.ui", self)

		# Menu Bar

		self.actionDir.triggered.connect(self.on_triggered_menu_dir)
		self.actionNew.triggered.connect(self.on_triggered_menu_new)
		self.actionOpen.triggered.connect(self.on_triggered_menu_open)
		self.actionSave.triggered.connect(self.on_triggered_menu_save)
		self.actionExit.triggered.connect(self.on_triggered_menu_exit)
		self.actionAbout.triggered.connect(self.on_triggered_menu_about)

		# Sign Up Tab

		self.comboBoxJoinIn.addItems([str(year) for year in range(1991, 2019, 1)])
		self.comboBoxJoinIn.setCurrentIndex(0)
		self.pushButtonSignUp.clicked.connect(self.on_clicked_button_signup)

		table_header = ["First Name", "Last Name", "Email", "Birthday", "Gender", "Join In"]
		self.tableWidgetUsers.setColumnCount(len(table_header))
		self.tableWidgetUsers.setHorizontalHeaderLabels(table_header)
		for idx, _ in enumerate(table_header):
			self.tableWidgetUsers.setColumnWidth(idx, 90)

		self.pushButtonGetTableSelected.clicked.connect(self.on_clicked_table_users)

		# Sign In Tab

		self.pushButtonSignIn.clicked.connect(self.on_clicked_button_signin)

		return

	def is_default_style(self):
		return QApplication.instance().style().metaObject().className() == "QWindowsVistaStyle"

	def on_triggered_menu_dir(self):
		file_path = DFDialog.select_directory(self, self.is_default_style())
		print(f"Select Directory `{file_path}`")
		return

	def on_triggered_menu_new(self):
		file_path = DFDialog.select_files(self, self.is_default_style())
		print(f"Select Files `{file_path}`")
		return

	def on_triggered_menu_open(self):
		file_path = DFDialog.select_file(self, self.is_default_style())
		print(f"Select File `{file_path}`")
		return

	def on_triggered_menu_save(self):
		file_path = DFDialog.save_file(self, self.is_default_style())
		print(f"Save File `{file_path}`")
		return

	def on_triggered_menu_exit(self):
		return self.close()

	def on_triggered_menu_about(self):
		self.about_dialog = AboutDlg()
		response = self.about_dialog.exec_()
		print(f"{self.about_dialog.__class__.__name__} {self.about_dialog.variable} {response}")
		return

	def on_clicked_button_signup(self):
		first_name = self.lineEditFirstName.text()
		last_name = self.lineEditLastName.text()
		email = self.lineEditEmail.text()
		DOB = self.dateEditDOB.date()
		birthday = (DOB.year(), DOB.month(), DOB.day())
		gender = self.buttonGroupGender.checkedButton().text()
		join_in = self.comboBoxJoinIn.currentText()

		user = {
			"first_name": first_name,
			"last_name": last_name,
			"email": email,
			"birthday": birthday,
			"gender": gender,
			"join_in": join_in
		}

		row = self.tableWidgetUsers.rowCount()
		self.tableWidgetUsers.setRowCount(row + 1)

		for col, val in enumerate(user.values()):
			self.tableWidgetUsers.setItem(row, col, QTableWidgetItem(str(val)))
		self.tableWidgetUsers.resizeRowsToContents()

		print(user)

		return

	def on_clicked_button_signin(self):
		email = self.lineEditEmail_2.text()
		optpin = self.lineEditOPT.text()
		print(f"{email} - {optpin}")
		return

	def on_clicked_table_users(self):
		for item in self.tableWidgetUsers.selectedItems():
			print(item.row(), item.column(), item.text())
		return
