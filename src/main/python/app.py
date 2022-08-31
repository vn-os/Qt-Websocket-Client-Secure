import os
os.environ["PATH"] += os.pathsep if os.environ["PATH"][-1] != os.pathsep else ""
os.environ["PATH"] += os.pathsep.join([os.getcwd()])

import sys
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from main import Window

# import qdarkstyle

# import qtmodern.styles
# import qtmodern.windows

# import qtstylish

# from qt_material import apply_stylesheet

if __name__ == "__main__":
	app_context = ApplicationContext()
	app = app_context.app
	win = Window(app_context)

	app.setStyle("fusion")
	
	# app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

	# qtmodern.styles.dark(app)
	# win = qtmodern.windows.ModernWindow(win)

	# app.setStyleSheet(qtstylish.light())

	# apply_stylesheet(app, theme='dark_teal.xml')

	win.show()

	sys.exit(app.exec_())
