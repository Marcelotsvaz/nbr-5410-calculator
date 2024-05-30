'''
Qt application entry point.
'''



import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLibraryInfo, QLocale

from nbr_5410_calculator.ui import MainWindow



def main() -> None:
	'''
	Entry point.
	'''
	
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



if __name__ == '__main__':
	main()