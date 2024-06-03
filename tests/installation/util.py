'''
Utility functions for `nbr_5410_calculator.installation` tests.
'''

from uuid import UUID
from nbr_5410_calculator.installation.circuit import (
	Circuit,
	LoadType,
	Supply,
	UpstreamCircuit,
	WireInsulation,
	WireMaterial,
	WireType,
)
from nbr_5410_calculator.installation.conduitRun import ConduitRun, ReferenceMethod
from nbr_5410_calculator.installation.project import Project



type jsonType = (
	dict[str, jsonType | str | int | float | None] | list[jsonType | str | int | float | None]
)



# 
# Models.
#-------------------------------------------------------------------------------
def createLoadType() -> LoadType:
	'''
	Create instance of `LoadType`.
	'''
	
	return LoadType(
		demandFactor		= 1.0,
		minimumWireSection	= 2.5,
		name				= 'Power',
		uuid				= UUID( '52cc8cf9-e0b3-4adc-aa76-5248d4c7787b' ),
	)


def createSupply() -> Supply:
	'''
	Create instance of `Supply`.
	'''
	
	return Supply(
		uuid				= UUID( '13cb4131-69c7-4483-b23c-e820a18d7ebf' ),
		voltage				= 100,
	)


def createWireType() -> WireType:
	'''
	Create instance of `WireType`.
	'''
	
	return WireType(
		insulation			= WireInsulation.PVC,
		material			= WireMaterial.COPPER,
		uuid				= UUID( '31373e68-bb79-44b9-9227-c87ff4f46db3' ),
	)


def createCircuit( conduitRun: ConduitRun ) -> Circuit:
	'''
	Create instance of `Circuit`.
	'''
	
	circuit = Circuit(
		conduitRun			= conduitRun,
		length				= 10.0,
		loadPower			= 5000,
		loadType			= createLoadType(),
		name				= 'Test Circuit',
		supply				= createSupply(),
		uuid				= UUID( 'e3f9a216-774e-46ee-986a-190abdb37b32' ),
		wireType			= createWireType(),
	)
	
	conduitRun.circuits.append( circuit )
	
	return circuit


def createUpstreamCircuit( conduitRun: ConduitRun ) -> UpstreamCircuit:
	'''
	Create instance of `UpstreamCircuit`.
	'''
	
	circuit = UpstreamCircuit(
		circuits			= [ createCircuit( conduitRun ) ] * 3,
		conduitRun			= conduitRun,
		length				= 10.0,
		loadType			= createLoadType(),
		name				= 'Test Upstream Circuit',
		supply				= createSupply(),
		uuid				= UUID( 'be773608-605f-46a8-89a9-366e4fe2bd1c' ),
		wireType			= createWireType(),
	)
	
	conduitRun.circuits.append( circuit )
	
	return circuit


def createConduitRun() -> ConduitRun:
	'''
	Create instance of `ConduitRun`.
	'''
	
	return ConduitRun(
		circuits			= [],
		length				= 10.0,
		name				= 'Test Conduit Run',
		referenceMethod		= ReferenceMethod.B1,
		temperature			= 30,
		uuid				= UUID( 'f4f3bd7c-c818-4ffc-a776-212469d8ba16' ),
	)


def createProject() -> Project:
	'''
	Create instance of `Project`.
	'''
	
	conduitRun = createConduitRun()
	
	project = Project(
		circuits			= [ createCircuit( conduitRun ) ] * 3,
		conduitRuns			= [ conduitRun ] * 3,
		name				= 'Test Project',
		uuid				= UUID( 'd1019f95-f48d-4a66-b1c3-681c802d396a' ),
	)
	
	return project



# 
# JSON.
#-------------------------------------------------------------------------------
def createLoadTypeDict() -> jsonType:
	'''
	Create JSON dict for `LoadType`.
	'''
	
	return {
		'demandFactor': 1.0,
		'minimumWireSection': 2.5,
		'name': 'Power',
		'uuid': '52cc8cf9-e0b3-4adc-aa76-5248d4c7787b',
	}


def createSupplyDict() -> jsonType:
	'''
	Create JSON dict for `Supply`.
	'''
	
	return {
		'hasGround': True,
		'hasNeutral': True,
		'phases': 1,
		'uuid': '13cb4131-69c7-4483-b23c-e820a18d7ebf',
		'voltage': 100,
	}


def createWireTypeDict() -> jsonType:
	'''
	Create JSON dict for `WireType`.
	'''
	
	return {
		'insulation': WireInsulation.PVC,
		'material': WireMaterial.COPPER,
		'uuid': '31373e68-bb79-44b9-9227-c87ff4f46db3',
	}


def createCircuitDict() -> jsonType:
	'''
	Create JSON dict for `Circuit`.
	'''
	
	return {
		'description': '',
		'length': 10.0,
		'loadPower': 5000.0,
		'loadType': createLoadTypeDict(),
		'name': 'Test Circuit',
		'supply': createSupplyDict(),
		'uuid': 'e3f9a216-774e-46ee-986a-190abdb37b32',
		'wireType': createWireTypeDict(),
	}


def createUpstreamCircuitDict( circuits: list[jsonType] ) -> jsonType:
	'''
	Create JSON dict for `UpstreamCircuit`.
	'''
	
	return {
		'circuits': [ *circuits ],
		'description': '',
		'length': 10.0,
		'loadType': createLoadTypeDict(),
		'name': 'Test Upstream Circuit',
		'supply': createSupplyDict(),
		'uuid': 'be773608-605f-46a8-89a9-366e4fe2bd1c',
		'wireType': createWireTypeDict(),
	}


def createConduitRunDict( circuits: list[jsonType] ) -> jsonType:
	'''
	Create JSON dict for `ConduitRun`.
	'''
	
	return {
		'circuits': [ *circuits ],
		'length': 10.0,
		'name': 'Test Conduit Run',
		'referenceMethod': ReferenceMethod.B1,
		'temperature': 30,
		'uuid': 'f4f3bd7c-c818-4ffc-a776-212469d8ba16',
	}


def createProjectDict( circuits: list[jsonType] ) -> jsonType:
	'''
	Create JSON dict for `Project`.
	'''
	
	return {
		'circuits': [ *circuits ],
		'conduitRuns': [ createConduitRunDict( [ circuit ] ) for circuit in circuits ],
		'defaultConduitRun': None,
		'defaultLoadType': None,
		'defaultSupply': None,
		'defaultWireType': None,
		'loadTypes': [],
		'name': 'Test Project',
		'supplies': [],
		'uuid': 'd1019f95-f48d-4a66-b1c3-681c802d396a',
		'wireTypes': [],
	}