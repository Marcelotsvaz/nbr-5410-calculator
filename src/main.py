# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale

from ui import MainWindow



if __name__ == '__main__':
	app = QApplication( sys.argv )
	
	translator = QTranslator()
	if translator.load( QLocale(), 'app', '_', 'share/translations/' ):
		app.installTranslator( translator )
	
	window = MainWindow()
	window.show()

	sys.exit( app.exec() )