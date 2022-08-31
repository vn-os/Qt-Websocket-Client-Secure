import os
os.environ["PATH"] += os.pathsep if os.environ["PATH"][-1] != os.pathsep else ""
os.environ["PATH"] += os.pathsep.join([os.getcwd()])

import sys
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from main import Window

# import qdarkstyle

# import qtmodern.styles
# import qtmodern.windows

if __name__ == "__main__":
	app = ApplicationContext()
	win = Window(app)

	app.app.setStyle("fusion")
	
	# app.app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

	# qtmodern.styles.dark(app.app)
	# win = qtmodern.windows.ModernWindow(win)

	win.show()

	sys.exit(app.app.exec_())
