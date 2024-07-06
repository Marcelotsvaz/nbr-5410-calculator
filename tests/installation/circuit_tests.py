# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import override
from unittest import TestCase

from nbr_5410_calculator.installation.circuit import Circuit, UpstreamCircuit
from tests.installation.util import (
	createCircuit,
	createCircuitDict,
	createConduitRun,
	createUpstreamCircuit,
	createUpstreamCircuitDict,
)



class BaseCircuitTests( TestCase ):
	'''
	Base class for all `Circuit` tests.
	'''
	
	@override
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.circuit = createCircuit( createConduitRun() )



class CircuitBasicTests( BaseCircuitTests ):
	'''
	Basic tests for `Circuit` class.
	'''
	
	def testCurrent( self ) -> None:
		'''
		Test `current` property.
		'''
		
		self.assertEqual( self.circuit.current, 50.0 )



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
		
		_ = createCircuit( self.circuit.conduitRun )
		self.circuit.conduitRun.temperature = 40
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
		
		_ = createCircuit( self.circuit.conduitRun )
		self.circuit.conduitRun.temperature = 40
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
		
		_ = createCircuit( self.circuit.conduitRun )
		self.circuit.conduitRun.temperature = 40
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
		
		self.assertEqual( self.circuit.model_dump(), createCircuitDict() )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		self.assertEqual( Circuit.model_validate( createCircuitDict() ), self.circuit )



class UpstreamCircuitTests( BaseCircuitTests ):
	'''
	Basic tests for `UpstreamCircuit` class.
	'''
	
	@override
	def setUp( self ) -> None:
		super().setUp()
		
		self.upstreamCircuit = createUpstreamCircuit( createConduitRun() )
		self.upstreamCircuitDict = createUpstreamCircuitDict( [ createCircuitDict() ] * 3 )
	
	
	def testTotalPower( self ) -> None:
		'''
		Total power should be the sum of the power of all downstream circuits.
		'''
		
		self.assertEqual( self.upstreamCircuit.power, 15_000.0 )
	
	
	def testTotalPowerWithDemandFactor( self ) -> None:
		'''
		Total power should be the sum of the power of all downstream circuits, corrected by each
		circuit's demand factor.
		'''
		
		self.upstreamCircuit.circuits[0].loadType.demandFactor = 0.5
		self.assertEqual( self.upstreamCircuit.power, 7_500.0 )
	
	
	def testSerialize( self ) -> None:
		'''
		Test serialization.
		'''
		
		self.assertEqual( self.upstreamCircuit.model_dump(), self.upstreamCircuitDict )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		self.assertEqual(
			UpstreamCircuit.model_validate( self.upstreamCircuitDict ),
			self.upstreamCircuit,
		)