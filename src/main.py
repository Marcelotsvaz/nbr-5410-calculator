# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLibraryInfo, QLocale

from ui import MainWindow



if __name__ == '__main__':
	app = QApplication( sys.argv )
	
	# Qt translations.
	translator = QTranslator( app )
	path = QLibraryInfo.path( QLibraryInfo.LibraryPath.TranslationsPath )
	if translator.load( QLocale(), 'qtbase', '_', path ):
		app.installTranslator( translator )
	
	# App translations.
	translator = QTranslator( app )
	if translator.load( QLocale(), 'app', '_', 'share/translations/' ):
		app.installTranslator( translator )
	
	window = MainWindow()
	window.show()

	sys.exit( app.exec() )