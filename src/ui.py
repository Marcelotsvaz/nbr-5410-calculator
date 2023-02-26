# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from jsons import loads, dumps	# pyright: ignore [reportUnknownVariableType]

from UiMainWindow import Ui_mainWindow as UiMainWindow
from installation.project import Project



class MainWindow( QMainWindow, UiMainWindow ):
	'''
	Main application window.
	'''
	
	def __init__( self ) -> None:
		'''
		Setup main application window.
		'''
		
		super().__init__()
		self.setupUi( self )	# pyright: ignore [reportUnknownMemberType]
		
		self.setProject( Project( 'New project', [] ) )
	
	
	def setProject( self, project: Project ):
		'''
		Set the current project, cascading changes to all models and views.
		'''
		
		self.project = project
		self.circuitsTableView.setDatasource( project.circuits )
	
	
	@Slot()
	def newProject( self ) -> None:
		'''
		Create a new empty project.
		'''
		
		self.setProject( Project( 'New project', [] ) )
	
	
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