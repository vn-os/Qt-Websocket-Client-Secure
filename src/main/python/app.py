import os
os.environ["PATH"] += os.pathsep if os.environ["PATH"][-1] != os.pathsep else ""
os.environ["PATH"] += os.pathsep.join([os.getcwd()])

import sys, qdarkstyle
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from main import Window

if __name__ == "__main__":
	app = ApplicationContext()
	app.app.setStyle("fusion")
	# app.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
	# app.PyQt5.QtWidgets.QStyleFactory.keys()

	window = Window(app)
	window.show()

	sys.exit(app.app.exec_())
