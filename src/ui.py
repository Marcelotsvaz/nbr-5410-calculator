# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtWidgets import QMainWindow

from UiMainWindow import Ui_mainWindow as UiMainWindow

from models import CircuitModel
from installation.circuit import (
	LoadType, WireMaterial, WireInsulation, WireType, ReferenceMethod, WireConfiguration, Circuit
)



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
		
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		circuits = [
			Circuit(
				name				= 'Chuveiro',
				loadType			= LoadType.POWER,
				voltage				= 220,
				phases				= 2,
				grouping			= 1,
				length				= 10,
				referenceMethod		= ReferenceMethod.B1,
				wireConfiguration	= WireConfiguration.TWO,
				wireType			= wireType,
				temperature			= 35,
				power				= 8000,
			),
			Circuit(
				name				= 'Torneira Elétrica',
				loadType			= LoadType.POWER,
				voltage				= 220,
				phases				= 2,
				grouping			= 1,
				length				= 15,
				referenceMethod		= ReferenceMethod.B1,
				wireConfiguration	= WireConfiguration.TWO,
				wireType			= wireType,
				temperature			= 35,
				power				= 6000,
			),
			Circuit(
				name				= 'Iluminação',
				loadType			= LoadType.LIGHTING,
				voltage				= 220,
				phases				= 2,
				grouping			= 1,
				length				= 15,
				referenceMethod		= ReferenceMethod.B1,
				wireConfiguration	= WireConfiguration.TWO,
				wireType			= wireType,
				temperature			= 35,
				power				= 500,
			),
		]
		
		self.model = CircuitModel( circuits )
		self.tableView.setModel( self.model )