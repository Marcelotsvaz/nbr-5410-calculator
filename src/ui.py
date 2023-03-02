# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QMainWindow, QFileDialog, QMessageBox
from jsons import loads, dumps

from UiMainWindow import Ui_mainWindow as UiMainWindow
from installation.project import Project



class MainWindow( QMainWindow, UiMainWindow ):
	'''
	Main application window.
	'''
	
	def __init__( self, parent: QWidget | None = None ) -> None:
		'''
		Setup main application window.
		'''
		
		super().__init__( parent )
		self.setupUi( self )	# pyright: ignore [reportUnknownMemberType]
		
		self.newProject()
	
	
	def setProject( self, project: Project ):
		'''
		Set the current project, cascading changes to all models and views.
		'''
		
		self.project = project	# pylint: disable = attribute-defined-outside-init
		self.circuitsTableView.setDatasource( project.circuits )
		self.circuitsTableView.resizeColumnsToContents()
	
	
	@Slot()
	def newProject( self ) -> None:
		'''
		Create a new empty project.
		'''
		
		self.setProject( Project( 'New project', [] ) )
		self.circuitsTableView.newCircuit()
		self.circuitsTableView.resizeColumnsToContents()
	
	
	@Slot()
	def loadProject( self ) -> None:
		'''
		Load a project from a file in JSON format.
		'''
		
		fileName: str = QFileDialog().getOpenFileName(	# pyright: ignore [ reportUnknownMemberType ]
			self,
			filter = 'Project files (*.json)',
			caption = 'Open Project',
		)[0]
		
		if not fileName:
			return
		
		try:
			with open( fileName ) as file:
				project = loads( file.read(), Project )
			
			self.setProject( project )
		except FileNotFoundError as error:
			QMessageBox.critical( self, 'Error', f'{error}' )
	
	
	@Slot()
	def saveProject( self ) -> None:
		'''
		Save project to a file in JSON format.
		'''
		
		fileName: str = QFileDialog().getSaveFileName(	# pyright: ignore [ reportUnknownMemberType ]
			self,
			filter = 'Project files (*.json)',
			caption = 'Save Project As',
		)[0]
		
		if not fileName:
			return
		
		try:
			with open( fileName, 'w' ) as file:
				jsonOptions: dict[str, object] = {
					'indent': '\t',
					'sort_keys': True,
				}
				file.write( dumps( self.project, strip_properties = True, jdkwargs = jsonOptions ) )
		except PermissionError as error:
			QMessageBox.critical( self, 'Error', str( error ) )
	
	
	@Slot()
	def showAbout( self ) -> None:
		'''
		Show about dialog.
		'''
		
		QMessageBox.about( self, 'About NBR 5410 Calculator', 'Version 0.1.0' )