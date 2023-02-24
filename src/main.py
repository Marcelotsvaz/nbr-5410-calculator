# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import sys

from PySide6.QtWidgets import QApplication

from ui import MainWindow



if __name__ == '__main__':
	app = QApplication( sys.argv )

	window = MainWindow()
	window.show()

	sys.exit( app.exec() )