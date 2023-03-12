# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase

from .circuit import (
	Supply,
	LoadType,
	WireMaterial,
	WireInsulation,
	WireType,
	ReferenceMethod,
	Circuit,
	UpstreamCircuit,
	ProjectError,
)



class BaseCircuitTests( TestCase ):
	'''
	Base class for all `Circuit` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.loadType = LoadType( 'Power', 2.5, 1.0 )
		self.supply = Supply( 100, 1 )
		self.wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		self.circuit = Circuit(
			grouping		= 1,
			length			= 10.0,
			loadType		= self.loadType,
			name			= 'Test Circuit',
			loadPower		= 5000,
			referenceMethod	= ReferenceMethod.B1,
			supply			= self.supply,
			temperature		= 30,
			wireType		= self.wireType,
		)



class CircuitBasicTests( BaseCircuitTests ):
	'''
	Basic tests for `Circuit` class.
	'''
	
	def testCurrent( self ) -> None:
		'''
		Test `current` property.
		'''
		
		self.assertEqual( self.circuit.current, 50.0 )
	
	
	def testCorrectedCurrent( self ) -> None:
		'''
		Test `correctedCurrent` property.
		'''
		
		self.assertEqual( self.circuit.correctedCurrent, 50.0 )
	
	
	def testTemperatureCorrection( self ) -> None:
		'''
		Test temperature correction with round value.
		'''
		
		self.circuit.temperature = 55
		
		self.assertAlmostEqual( self.circuit.correctedCurrent, 81.967213, 6 )
	
	
	def testTemperatureCorrectionInterpolation( self ) -> None:
		'''
		Test temperature correction with interpolated value.
		'''
		
		self.circuit.temperature = 58
		
		self.assertAlmostEqual( self.circuit.correctedCurrent, 91.911765, 6 )
	
	
	def testTemperatureCorrectionBelowMinimum( self ) -> None:
		'''
		Temperatures below minimum should use the factor for the lowest temperature available.
		'''
		
		self.circuit.temperature = -10
		
		self.assertAlmostEqual( self.circuit.correctedCurrent, 40.983607, 6 )
	
	
	def testTemperatureCorrectionAboveMaximum( self ) -> None:
		'''
		Temperatures above maximum for the given insulation type should raise an exception.
		'''
		
		self.circuit.temperature = 70
		
		with self.assertRaises( ProjectError ):
			_ = self.circuit.correctedCurrent



class CircuitWireTests( BaseCircuitTests ):
	'''
	Wire related tests for `Circuit` class.
	'''
	
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
	Tests for `Circuit` serialization with jsons.
	'''
	
	def setUp( self ) -> None:
		super().setUp()
		
		self.circuitJsonDict = {
			'description': None,
			'grouping': 1,
			'length': 10.0,
			'loadType': {
				'demandFactor': 1.0,
				'minimumWireSection': 2.5,
				'name': 'Power',
			},
			'name': 'Test Circuit',
			'loadPower': 5000,
			'referenceMethod': 'B1',
			'supply': {
				'voltage': 100,
				'phases': 1,
			},
			'temperature': 30,
			'wireType': {
				'insulation': 'PVC',
				'material': 'COPPER',
			},
		}
	
	
	def testSerializeCircuit( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		self.assertEqual( self.circuit.dump(), self.circuitJsonDict )
	
	
	def testDeserializeCircuit( self ) -> None:
		'''
		Test deserialization with jsons.load.
		'''
		
		self.assertEqual( Circuit.load( self.circuitJsonDict ), self.circuit )



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
			loadType		= self.loadType,
			name			= 'Test Upstream Circuit',
			referenceMethod	= ReferenceMethod.B1,
			supply			= self.supply,
			temperature		= 30,
			wireType		= self.wireType,
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
		
		self.loadType.demandFactor = 0.5
		self.assertEqual( self.upstreamCircuit.power, 25_000.0 )