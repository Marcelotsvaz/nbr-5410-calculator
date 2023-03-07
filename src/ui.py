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
from circuitsTab import CircuitsModel
from conduitsTab import ConduitRunsModel



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
		
		self.circuitsTableView.setModel( CircuitsModel( project.circuits, self ) )
		self.circuitsTableView.resizeColumnsToContents()
		
		self.conduitsTableView.setModel( ConduitRunsModel( project.conduitRuns, self ) )
		self.conduitsTableView.resizeColumnsToContents()
	
	
	@Slot()
	def newProject( self ) -> None:
		'''
		Create a new empty project.
		'''
		
		self.setProject( Project( self.tr('New Project') ) )
		self.circuitsTableView.newItem()
		self.circuitsTableView.resizeColumnsToContents()
		
		self.conduitsTableView.newItem()
		self.conduitsTableView.resizeColumnsToContents()
	
	
	@Slot()
	def loadProject( self ) -> None:
		'''
		Load a project from a file in JSON format.
		'''
		
		fileName: str = QFileDialog().getOpenFileName(	# pyright: ignore [ reportUnknownMemberType ]
			self,
			filter = self.tr('Project files (*.json)'),
			caption = self.tr('Open Project'),
		)[0]
		
		if not fileName:
			return
		
		try:
			with open( fileName ) as file:
				project = loads( file.read(), Project )
			
			self.setProject( project )
		except FileNotFoundError as error:
			QMessageBox.critical( self, self.tr('Error'), f'{error}' )
	
	
	@Slot()
	def saveProject( self ) -> None:
		'''
		Save project to a file in JSON format.
		'''
		
		fileName: str = QFileDialog().getSaveFileName(	# pyright: ignore [ reportUnknownMemberType ]
			self,
			filter = self.tr('Project files (*.json)'),
			caption = self.tr('Save Project As'),
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
			QMessageBox.critical( self, self.tr('Error'), str( error ) )
	
	
	@Slot()
	def showAbout( self ) -> None:
		'''
		Show about dialog.
		'''
		
		QMessageBox.about(
			self,
			self.tr('About NBR 5410 Calculator'),
			self.tr('Version {0}.').format( '0.1.0' )
		)
	
	
	# pylint: disable-next = useless-parent-delegation, invalid-name
	def tr( self, *args: str ) -> str:
		'''
		Translate string.
		Temporary fix for missing `tr` method in `QObject`.
		'''
		
		return super().tr( *args )	# pyright: ignore