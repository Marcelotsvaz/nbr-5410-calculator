# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QFileDialog
from pyjson5 import decode_io, encode

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
		
		# pylint: disable-next=line-too-long
		fileName: str = QFileDialog().getOpenFileName( self, filter = '*.json5' )[0]	# pyright: ignore [reportUnknownMemberType]
		with open( fileName ) as file:
			project = Project.fromJson( decode_io( file ) )
		
		self.setProject( project )
	
	
	@Slot()
	def saveProject( self ) -> None:
		'''
		Save project to a file in JSON format.
		'''
		
		# pylint: disable-next=line-too-long
		fileName: str = QFileDialog().getSaveFileName( self, filter = '*.json5' )[0]	# pyright: ignore [reportUnknownMemberType]
		with open( fileName, 'w' ) as file:
			json: str = encode( self.project.toJson() )	# pyright: ignore [reportGeneralTypeIssues]
			file.write( json )