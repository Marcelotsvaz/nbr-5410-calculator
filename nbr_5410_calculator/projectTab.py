'''
Models and view for the project tab.
'''

from typing import override

from PySide6.QtCore import QObject, Slot

from nbr_5410_calculator.generic_model_views.models import Field, GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericListView
from nbr_5410_calculator.installation.circuit import Supply, LoadType, WireMaterial, WireInsulation, WireType



# 
# Models
#-------------------------------------------------------------------------------
class SupplyModel( GenericItemModel[Supply] ):
	'''
	Map a list of `Supply`s to a `QListView`.
	'''
	
	@override
	def __init__( self, supplies: list[Supply], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'voltage', self.tr('Voltage') ),
		]
		
		super().__init__( fields, supplies, parent = parent )



class LoadTypeModel( GenericItemModel[LoadType] ):
	'''
	Map a list of `LoadType`s to a `QTableView`.
	'''
	
	@override
	def __init__( self, loadTypes: list[LoadType], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'name', self.tr('Name') ),
		]
		
		super().__init__( fields, loadTypes, parent = parent )



class WireTypeModel( GenericItemModel[WireType] ):
	'''
	Map a list of `WireType`s to a `QTableView`.
	'''
	
	@override
	def __init__( self, wireTypes: list[WireType], parent: QObject | None = None ) -> None:
		fields = [
			Field( 'material', self.tr('Material') ),
		]
		
		super().__init__( fields, wireTypes, parent = parent )



# 
# Views
#-------------------------------------------------------------------------------
class SupplyView( GenericListView[SupplyModel, Supply] ):
	'''
	`QListView` for `SupplyModel`.
	'''
	
	@Slot()
	def newSupply( self ) -> Supply:
		'''
		Create new `Supply`.
		'''
		
		supply = Supply(
			voltage = 127,
		)
		
		self.appendItem( supply )
		
		return supply



class LoadTypeView( GenericListView[LoadTypeModel, LoadType] ):
	'''
	`QListView` for `LoadTypeModel`.
	'''
	
	@Slot()
	def newLoadType( self ) -> LoadType:
		'''
		Create new `LoadType`.
		'''
		
		loadType = LoadType(
			name = self.tr('Power'),
			minimumWireSection = 2.5,
			demandFactor = 1.0,
		)
		
		self.appendItem( loadType )
		
		return loadType



class WireTypeView( GenericListView[WireTypeModel, WireType] ):
	'''
	`QListView` for `WireTypeModel`.
	'''
	
	@Slot()
	def newWireType( self ) -> WireType:
		'''
		Create new `WireType`.
		'''
		
		wireType = WireType(
			material = WireMaterial.COPPER,
			insulation = WireInsulation.PVC,
		)
		
		self.appendItem( wireType )
		
		return wireType