# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import QObject

from genericTreeView import Field, GenericItemModel
from installation.circuit import (
	Supply,
	LoadType,
	WireMaterial,
	WireInsulation,
	WireType,
	ReferenceMethod,
	BaseCircuit,
	Circuit,
)



class CircuitsModel( GenericItemModel[BaseCircuit] ):
	'''
	Map a list of `Circuit`s to a QTableView.
	'''
	
	def __init__( self, circuits: list[BaseCircuit], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'name',						self.tr('Name') ),
			Field( 'supply',					self.tr('Supply') ),
			Field( 'loadType.name',				self.tr('Load Type'),		setter = 'loadType' ),
			Field( 'power',						self.tr('Power'),			format = ',', suffix = ' VA' ),
			Field( 'referenceMethod',			self.tr('Ref. Method') ),
			Field( 'temperature',				self.tr('Temperature'),		suffix = '°C' ),
			Field( 'grouping',					self.tr('Grouping') ),
			Field( 'wireType',					self.tr('Wire Type') ),
			Field( 'length',					self.tr('Length'),			format = ',', suffix = ' m' ),
			Field( 'current',					self.tr('Current'),			False, format = ',.1f', suffix = ' A' ),
			Field( 'breaker.current',			self.tr('Breaker'),			False, suffix = ' A' ),
			Field( 'wire.capacity',				self.tr('Wire Capacity'),	False, format = ',.1f', suffix = ' A' ),
			Field( 'voltageDrop',				self.tr('Voltage Drop'),	False, format = '.1%' ),
			Field( 'wire.section',				self.tr('Wire Section'),	False, format = ',', suffix = ' mm²' ),
		]
		childListName = 'circuits'
		
		super().__init__( fields, circuits, childListName, parent )
	
	
	def newItem( self ) -> BaseCircuit:
		'''
		Return a new `Circuit` to be used with `insertRows`.
		'''
		
		loadType = LoadType( 'Power', 2.5, 1.0 )
		supply = Supply( 127, 1 )
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		circuit = Circuit(
			grouping		= 1,
			length			= 10.0,
			loadType		= loadType,
			name			= self.tr('New Circuit'),
			loadPower		= 1000,
			referenceMethod	= ReferenceMethod.B1,
			supply			= supply,
			temperature		= 30,
			wireType		= wireType,
		)
		
		return circuit