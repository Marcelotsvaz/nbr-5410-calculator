# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtWidgets import QMainWindow, QFileDialog
from PySide6.QtCore import Slot
from pyjson5 import decode_io, encode

from UiMainWindow import Ui_mainWindow as UiMainWindow

from models import CircuitModel
from installation.circuit import Circuit



class MainWindow( QMainWindow, UiMainWindow ):
	'''
	Main application window.
	'''
	
	def __init__( self ) -> None:
		'''
		Setup main application window.
		'''
		
		super().__init__()
		self.setupUi( self )
		self.model = CircuitModel( [] )
		self.tableView.setModel( self.model )
	
	
	@Slot()
	def loadProject( self ) -> None:
		'''
		Load a project from a file in JSON format.
		'''
		
		circuits: list[Circuit] = []
		
		fileName = QFileDialog().getOpenFileName( self, filter = '*.json5' )[0]
		with open( fileName ) as file:
			for circuit in decode_io( file )['circuits']:
				circuits.append( Circuit.fromJson( circuit ) )
		
		self.model.setDatasource( circuits )
	
	
	@Slot()
	def saveProject( self ) -> None:
		'''
		Save project to a file in JSON format.
		'''
		
		circuitsJson = {
			'circuits': [ circuit.toJson() for circuit in self.model.circuits ]
		}
		
		fileName = QFileDialog().getSaveFileName( self, filter = '*.json5' )[0]
		with open( fileName, 'w' ) as file:
			file.write( encode( circuitsJson ) )