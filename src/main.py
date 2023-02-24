# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from installation.circuit import (
	LoadType, WireMaterial, WireInsulation, WireType, ReferenceMethod, WireConfiguration, Circuit
)



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


for circuit in circuits:
	print( f'{circuit.name}: Current: {circuit.current:.2f}A Corrected Current: {circuit.correctedCurrent:.2f}A {circuit.wire} {circuit.breaker}' )