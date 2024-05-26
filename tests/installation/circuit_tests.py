# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase
from uuid import UUID
from typing import Any

from nbr_5410_calculator.installation.circuit import (
	Circuit,
	LoadType,
	ProjectError,
	ReferenceMethod,
	Supply,
	UpstreamCircuit,
	WireInsulation,
	WireMaterial,
	WireType,
)



def createCircuit() -> Circuit:
	'''
	Create instance of `Circuit`.
	'''
	
	loadType = LoadType(
		demandFactor		= 1.0,
		minimumWireSection	= 2.5,
		name				= 'Power',
		uuid				= UUID( '52cc8cf9-e0b3-4adc-aa76-5248d4c7787b' ),
	)
	supply = Supply(
		uuid				= UUID( '13cb4131-69c7-4483-b23c-e820a18d7ebf' ),
		voltage				= 100,
	)
	wireType = WireType(
		insulation			= WireInsulation.PVC,
		material			= WireMaterial.COPPER,
		uuid				= UUID( '31373e68-bb79-44b9-9227-c87ff4f46db3' ),
	)
	circuit = Circuit(
		grouping			= 1,
		length				= 10.0,
		loadPower			= 5000,
		loadType			= loadType,
		name				= 'Test Circuit',
		referenceMethod		= ReferenceMethod.B1,
		supply				= supply,
		temperature			= 30,
		uuid				= UUID( 'e3f9a216-774e-46ee-986a-190abdb37b32' ),
		wireType			= wireType,
	)
	
	return circuit



def createCircuitJsonDict() -> dict[str, Any]:
	'''
	Create JSON dict for `Circuit`.
	'''
	
	circuitJsonDict = {
		'description': '',
		'grouping': 1,
		'length': 10.0,
		'loadPower': 5000,
		'loadType': {
			'demandFactor': 1.0,
			'minimumWireSection': 2.5,
			'name': 'Power',
			'uuid': UUID( '52cc8cf9-e0b3-4adc-aa76-5248d4c7787b' ),
		},
		'name': 'Test Circuit',
		'referenceMethod': ReferenceMethod.B1,
		'supply': {
			'hasGround': True,
			'hasNeutral': True,
			'phases': 1,
			'uuid': UUID( '13cb4131-69c7-4483-b23c-e820a18d7ebf' ),
			'voltage': 100,
		},
		'temperature': 30,
		'uuid': UUID( 'e3f9a216-774e-46ee-986a-190abdb37b32' ),
		'wireType': {
			'insulation': WireInsulation.PVC,
			'material': WireMaterial.COPPER,
			'uuid': UUID( '31373e68-bb79-44b9-9227-c87ff4f46db3' ),
		},
	}
	
	return circuitJsonDict



class BaseCircuitTests( TestCase ):
	'''
	Base class for all `Circuit` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.circuit = createCircuit()



class CircuitBasicTests( BaseCircuitTests ):
	'''
	Basic tests for `Circuit` class.
	'''
	
	def testCurrent( self ) -> None:
		'''
		Test `current` property.
		'''
		
		self.assertEqual( self.circuit.current, 50.0 )



class CircuitCorrectionFactorTests( BaseCircuitTests ):
	'''
	Test `Circuit` correction factor by temperature and grouping.
	'''
	
	def testTemperatureCorrection( self ) -> None:
		'''
		Test temperature correction with round value.
		'''
		
		self.circuit.temperature = 55
		
		self.assertEqual( self.circuit.correctionFactor, 0.61 )
	
	
	def testTemperatureCorrectionInterpolation( self ) -> None:
		'''
		Test temperature correction with interpolated value.
		'''
		
		self.circuit.temperature = 58
		
		self.assertEqual( self.circuit.correctionFactor, 0.544 )
	
	
	def testTemperatureCorrectionBelowMinimum( self ) -> None:
		'''
		Temperatures below minimum should use the factor for the lowest temperature available.
		'''
		
		self.circuit.temperature = -10
		
		self.assertEqual( self.circuit.correctionFactor, 1.22 )
	
	
	def testTemperatureCorrectionAboveMaximum( self ) -> None:
		'''
		Temperatures above maximum for the given insulation type should raise an exception.
		'''
		
		self.circuit.temperature = 70
		
		with self.assertRaises( ProjectError ):
			_ = self.circuit.correctionFactor



class CircuitWireTests( BaseCircuitTests ):
	'''
	Wire related tests for `Circuit` class.
	'''
	
	def testResistancePerMeter( self ) -> None:
		'''
		Calculate resistance per meter from section and resistivity.
		'''
		
		self.assertAlmostEqual( self.circuit.wire.resistancePerMeter, 0.001720, 6 )
	
	
	def testExternalSection( self ) -> None:
		'''
		Calculate external section from external diameter.
		'''
		
		self.assertAlmostEqual( self.circuit.wire.externalSection, 27.339710, 6 )
	
	
	def testSectionByMinimumSection( self ) -> None:
		'''
		Minimum wire section given load type.
		'''
		
		self.circuit.power = 1000
		self.assertEqual( self.circuit.wire.section, 2.5 )
	
	
	def testSectionByCapacity( self ) -> None:
		'''
		Wire section given reference method and wire configuration.
		'''
		
		self.assertEqual( self.circuit.wire.section, 10.0 )
	
	
	def testSectionByCorrectedCapacity( self ) -> None:
		'''
		Wire section with capacity corrected for temperature and grouping.
		'''
		
		self.circuit.grouping = 2
		self.circuit.temperature = 40
		self.assertEqual( self.circuit.wire.section, 16.0 )
	
	
	def testSectionByVoltageDrop( self ) -> None:
		'''
		Wire section limited by voltage drop.
		'''
		
		self.circuit.length = 25
		self.assertEqual( self.circuit.wire.section, 16.0 )
	
	
	def testSectionByBreaker( self ) -> None:
		'''
		Wire section forced larger due to available breaker capacities.
		'''
		
		self.circuit.power = 5500
		self.assertEqual( self.circuit.wire.section, 16.0 )
	
	
	def testCapacity( self ) -> None:
		'''
		Wire capacity given reference method and wire configuration.
		'''
		
		self.assertEqual( self.circuit.wire.uncorrectedCapacity, 57.0 )
		self.assertEqual( self.circuit.wire.capacity, 57.0 )
	
	
	def testCorrectedCapacity( self ) -> None:
		'''
		Wire capacity corrected for temperature and grouping.
		'''
		
		self.circuit.grouping = 2
		self.circuit.temperature = 40
		self.assertEqual( self.circuit.wire.uncorrectedCapacity, 76.0 )
		self.assertAlmostEqual( self.circuit.wire.capacity, 52.896000, 6 )



class CircuitVoltageDropTests( BaseCircuitTests ):
	'''
	Voltage drop tests for `Circuit` class.
	'''
	
	def testVoltageDrop( self ) -> None:
		'''
		Test voltage drop.
		'''
		
		self.assertAlmostEqual( self.circuit.voltageDrop, 0.017200, 6 )



class CircuitBreakerTests( BaseCircuitTests ):
	'''
	Breaker related tests for `Circuit` class.
	'''
	
	def testBreaker( self ) -> None:
		'''
		Test if proper breaker is returned for the circuit.
		'''
		
		self.assertEqual( self.circuit.breaker.current, 50 )
	
	
	def testCorrectedBreaker( self ) -> None:
		'''
		Test if proper breaker is returned for the circuit when using correction factors.
		'''
		
		self.circuit.grouping = 2
		self.circuit.temperature = 40
		self.assertEqual( self.circuit.breaker.current, 50 )
	
	
	def testBreakerWhenWireSectionByBreaker( self ) -> None:
		'''
		Test breaker when wire section is determined by available breaker.
		'''
		
		self.circuit.power = 5500
		self.assertEqual( self.circuit.breaker.current, 63 )



class CircuitSerializationTests( BaseCircuitTests ):
	'''
	Tests for `Circuit` serialization with Pydantic.
	'''
	
	def testSerialize( self ) -> None:
		'''
		Test serialization.
		'''
		
		self.assertEqual( self.circuit.model_dump(), createCircuitJsonDict() )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		self.assertEqual( Circuit.model_validate( createCircuitJsonDict() ), self.circuit )



class UpstreamCircuitTests( BaseCircuitTests ):
	'''
	Basic tests for `UpstreamCircuit` class.
	'''
	
	def setUp( self ) -> None:
		super().setUp()
		
		self.upstreamCircuit = UpstreamCircuit(
			circuits		= [ self.circuit ] * 10,
			grouping		= 1,
			length			= 10.0,
			loadType		= self.circuit.loadType,
			name			= 'Test Upstream Circuit',
			referenceMethod	= ReferenceMethod.B1,
			supply			= self.circuit.supply,
			temperature		= 30,
			wireType		= self.circuit.wireType,
		)
	
	
	def testTotalPower( self ) -> None:
		'''
		Total power should be the sum of the power of all downstream circuits.
		'''
		
		self.assertEqual( self.upstreamCircuit.power, 50_000.0 )
	
	
	def testTotalPowerWithDemandFactor( self ) -> None:
		'''
		Total power should be the sum of the power of all downstream circuits, corrected by each
		circuit's demand factor.
		'''
		
		self.circuit.loadType.demandFactor = 0.5
		self.assertEqual( self.upstreamCircuit.power, 25_000.0 )