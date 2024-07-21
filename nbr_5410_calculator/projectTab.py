'''
Models and view for the project tab.
'''

from PySide6.QtCore import Slot

from nbr_5410_calculator.generic_model_views.models import GenericItemModel
from nbr_5410_calculator.generic_model_views.views import GenericTreeView
from nbr_5410_calculator.installation.circuit import (
	LoadType, 
	Supply, 
	WireInsulation, 
	WireMaterial, 
	WireType,
)



class SupplyView( GenericTreeView[GenericItemModel[Supply], Supply] ):
	'''
	List view of `Supply`.
	'''
	
	fieldOrder = {
		Supply: [
			'voltage',
			'phases',
			'hasNeutral',
			'hasGround',
		],
	}
	
	
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



class LoadTypeView( GenericTreeView[GenericItemModel[LoadType], LoadType] ):
	'''
	List view of `LoadType`.
	'''
	
	fieldOrder = {
		LoadType: [
			'name',
			'minimumWireSection',
			'demandFactor',
		],
	}
	
	
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



class WireTypeView( GenericTreeView[GenericItemModel[WireType], WireType] ):
	'''
	List view of `WireType`.
	'''
	
	fieldOrder = {
		WireType: [
			'material',
			'insulation',
		],
	}
	
	
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