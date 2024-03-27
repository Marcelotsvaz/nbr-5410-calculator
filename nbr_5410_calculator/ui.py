# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QMainWindow, QFileDialog, QMessageBox
from jsons import Verbosity

from nbr_5410_calculator.UiMainWindow import Ui_mainWindow as UiMainWindow
from nbr_5410_calculator.installation.project import Project
from nbr_5410_calculator.projectTab import SupplyModel, LoadTypeModel, WireTypeModel
from nbr_5410_calculator.circuitsTab import CircuitsModel
from nbr_5410_calculator.conduitsTab import ConduitRunsModel



class MainWindow( QMainWindow, UiMainWindow ):
	'''
	Main application window.
	'''
	
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		self.setupUi( self )	# pyright: ignore [reportUnknownMemberType]
		
		self.newProject()
	
	
	def setProject( self, project: Project ) -> None:
		'''
		Set the current project, cascading changes to all models and views.
		'''
		
		self.project = project	# pylint: disable = attribute-defined-outside-init
		
		self.suppliesListView.setModel( SupplyModel( project.supplies, self ) )
		self.loadTypesListView.setModel( LoadTypeModel( project.loadTypes, self ) )
		self.wireTypesListView.setModel( WireTypeModel( project.wireTypes, self ) )
		
		self.circuitsTreeView.setModel( CircuitsModel( project.circuits, self ) )
		self.circuitsTreeView.expandAll()
		self.circuitsTreeView.resizeColumnsToContents()
		
		self.conduitsTreeView.setModel( ConduitRunsModel( project.conduitRuns, self ) )
		self.conduitsTreeView.expandAll()
		self.conduitsTreeView.resizeColumnsToContents()
	
	
	@Slot()
	def newProject( self ) -> None:
		'''
		Create a new empty project.
		'''
		
		self.setProject( Project( self.tr('New Project') ) )
		
		self.suppliesListView.newItem()
		self.loadTypesListView.newItem()
		self.wireTypesListView.newItem()
		
		self.circuitsTreeView.newItem()
		self.circuitsTreeView.expandAll()
		self.circuitsTreeView.resizeColumnsToContents()
		
		self.conduitsTreeView.newItem()
		self.conduitsTreeView.expandAll()
		self.conduitsTreeView.resizeColumnsToContents()
	
	
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
				project = Project.loads( file.read() )
			
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
				file.write( self.project.dumps( verbose = Verbosity.WITH_CLASS_INFO ) )
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