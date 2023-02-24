# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from installation.circuit import (
	WireMaterial, WireInsulation, WireType, ReferenceMethod, WireConfiguration, Circuit
)



wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
circuits = [
	Circuit(
		name				= 'Chuveiro',
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
		name				= 'Torneira Elétrica Cozinha',
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
]


for circuit in circuits:
	print( f'{circuit.name}: Current: {circuit.current:.2f}A Project Current: {circuit.projectCurrent:.2f}A {circuit.wire} {circuit.breaker}' )