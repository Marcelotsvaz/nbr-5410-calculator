'''
Main window and project-level stuff.
'''

from typing import override

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QMainWindow, QFileDialog, QMessageBox

from nbr_5410_calculator.circuitsTab import CircuitsModel
from nbr_5410_calculator.generic_model_views.models import GenericItemModel
from nbr_5410_calculator.installation.circuit import BaseCircuit, LoadType, Supply, WireType
from nbr_5410_calculator.installation.conduitRun import ConduitRun
from nbr_5410_calculator.installation.project import Project
from nbr_5410_calculator.UiMainWindow import Ui_mainWindow as UiMainWindow



class MainWindow( QMainWindow, UiMainWindow ):
	'''
	Main application window.
	'''
	
	project: Project
	
	
	@override
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		self.setupUi( self )	# pyright: ignore [reportUnknownMemberType]
		
		self.newProject()
	
	
	def setProject( self, project: Project ) -> None:
		'''
		Set the current project, cascading changes to all models and views.
		'''
		
		self.project = project
		
		# Models.
		supplyModel = GenericItemModel( project.supplies, [ Supply ], self )
		loadTypeModel = GenericItemModel( project.loadTypes, [ LoadType ], self )
		wireTypeModel = GenericItemModel( project.wireTypes, [ WireType ], self )
		
		circuitsModel = CircuitsModel( project, self )
		
		conduitRunsModel = GenericItemModel( project.conduitRuns, [ ConduitRun, BaseCircuit ], self )
		
		# Views.
		self.suppliesListView.setModel( supplyModel )
		self.loadTypesListView.setModel( loadTypeModel )
		self.wireTypesListView.setModel( wireTypeModel )
		
		self.circuitsTreeView.setModel( circuitsModel )
		self.circuitsTreeView.expandAll()
		self.circuitsTreeView.resizeColumnsToContents()
		
		self.conduitsTreeView.setModel( conduitRunsModel )
		self.conduitsTreeView.expandAll()
		self.conduitsTreeView.resizeColumnsToContents()
		# self.unassignedCircuitsView.setModel( circuitsModel )
	
	
	@Slot()
	def newProject( self ) -> None:
		'''
		Create a new empty project.
		'''
		
		project = Project( name = self.tr('New Project') )
		
		self.setProject( project )
		
		project.defaultSupply = self.suppliesListView.newSupply()
		project.defaultLoadType = self.loadTypesListView.newLoadType()
		project.defaultWireType = self.wireTypesListView.newWireType()
		
		self.circuitsTreeView.newCircuit()
		self.circuitsTreeView.expandAll()
		self.circuitsTreeView.resizeColumnsToContents()
		
		self.conduitsTreeView.newConduitRun()
		self.conduitsTreeView.expandAll()
		self.conduitsTreeView.resizeColumnsToContents()
	
	
	@Slot()
	def loadProject( self ) -> None:
		'''
		Load a project from a file in JSON format.
		'''
		
		fileName = QFileDialog().getOpenFileName(
			self,
			filter = self.tr('Project files (*.json)'),
			caption = self.tr('Open Project'),
		)[0]
		
		if not fileName:
			return
		
		try:
			with open( fileName, 'rb' ) as file:
				project = Project.model_validate_json( file.read(), context = {} )
			
			self.setProject( project )
		except FileNotFoundError as error:
			QMessageBox.critical( self, self.tr('Error'), f'{error}' )
	
	
	@Slot()
	def saveProject( self ) -> None:
		'''
		Save project to a file in JSON format.
		'''
		
		fileName = QFileDialog().getSaveFileName(
			self,
			filter = self.tr('Project files (*.json)'),
			caption = self.tr('Save Project As'),
		)[0]
		
		if not fileName:
			return
		
		try:
			with open( fileName, 'wb' ) as file:
				file.write( self.project.model_dump_json().encode() )
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