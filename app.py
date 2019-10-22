import sys, qdarkstyle
from PyQt5.QtWidgets import QApplication

from main import Window

if __name__ == "__main__":
	app = QApplication(sys.argv)
	# app.setStyle("fusion")
	# app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
	# PyQt5.QtWidgets.QStyleFactory.keys()

	window = Window()
	window.show()

	sys.exit(app.exec_())