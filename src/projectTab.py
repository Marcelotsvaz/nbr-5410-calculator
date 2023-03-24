# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from PySide6.QtCore import QObject

from genericModelViews.models import Field, GenericItemModel
from installation.circuit import Supply, LoadType, WireMaterial, WireInsulation, WireType



class SupplyModel( GenericItemModel[Supply] ):
	'''
	Map a list of `Supply`s to a QListView.
	'''
	
	def __init__( self, supplies: list[Supply], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'voltage', self.tr('Voltage') ),
		]
		
		super().__init__( fields, supplies, parent = parent )
	
	
	def newItem( self ) -> Supply:
		'''
		Return a new `Supply` to be used with `insertRows`.
		'''
		
		supply = Supply( 127 )
		
		return supply



class LoadTypeModel( GenericItemModel[LoadType] ):
	'''
	Map a list of `LoadType`s to a QTableView.
	'''
	
	def __init__( self, loadTypes: list[LoadType], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'name', self.tr('Name') ),
		]
		
		super().__init__( fields, loadTypes, parent = parent )
	
	
	def newItem( self ) -> LoadType:
		'''
		Return a new `LoadType` to be used with `insertRows`.
		'''
		
		loadType = LoadType( 'Power', 2.5, 1.0 )
		
		return loadType



class WireTypeModel( GenericItemModel[WireType] ):
	'''
	Map a list of `WireType`s to a QTableView.
	'''
	
	def __init__( self, wireTypes: list[WireType], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'material', self.tr('Material') ),
		]
		
		super().__init__( fields, wireTypes, parent = parent )
	
	
	def newItem( self ) -> WireType:
		'''
		Return a new `WireType` to be used with `insertRows`.
		'''
		
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		
		return wireType