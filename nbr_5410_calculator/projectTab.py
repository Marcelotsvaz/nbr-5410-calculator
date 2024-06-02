'''
Models and view for the project tab.
'''

from PySide6.QtCore import Slot

from nbr_5410_calculator.generic_model_views.models import GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericListView
from nbr_5410_calculator.installation.circuit import (
	LoadType, 
	Supply, 
	WireInsulation, 
	WireMaterial, 
	WireType,
)



class SupplyView( GenericListView[GenericItemModel[Supply], Supply] ):
	'''
	`QListView` for `SupplyModel`.
	'''
	
	fieldOrder = [
		'voltage'
	]
	
	
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



class LoadTypeView( GenericListView[GenericItemModel[LoadType], LoadType] ):
	'''
	`QListView` for `LoadTypeModel`.
	'''
	
	fieldOrder = [
		'name'
	]
	
	
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



class WireTypeView( GenericListView[GenericItemModel[WireType], WireType] ):
	'''
	`QListView` for `WireTypeModel`.
	'''
	
	fieldOrder = [
		'material'
	]
	
	
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