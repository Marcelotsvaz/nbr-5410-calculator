# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase

from jsons import load, dump	# pyright: ignore [reportUnknownVariableType]

from .circuit import (
	LoadType,
	WireMaterial,
	WireInsulation,
	WireType,
	ReferenceMethod,
	WireConfiguration,
	Circuit,
	Wire,
	Breaker,
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
		
		self.wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		self.circuit = Circuit(
			grouping			= 1,
			length				= 10.0,
			loadType			= LoadType.POWER,
			name				= 'Test Circuit',
			phases				= 1,
			power				= 5000.0,
			referenceMethod		= ReferenceMethod.B1,
			temperature			= 30,
			voltage				= 100,
			wireConfiguration	= WireConfiguration.TWO,
			wireType			= self.wireType,
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
	
	
	def testWire( self ) -> None:
		'''
		Test if proper wire section is returned for the specified reference method.
		'''
		
		self.assertEqual( self.circuit.wire, Wire( self.wireType, 10.0 ) )
	
	
	def testMinimumWireSection( self ) -> None:
		'''
		Test if minimum wire section is respected.
		'''
		
		self.circuit.power = 1000
		
		self.assertEqual( self.circuit.wire, Wire( self.wireType, 2.5 ) )
	
	
	def testBreaker( self ) -> None:
		'''
		Test if proper breaker is returned for the circuit.
		'''
		
		self.assertEqual( self.circuit.breaker, Breaker( 50 ) )
	
	
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



class CircuitSerializationTests( BaseCircuitTests ):
	'''
	Tests for `Circuit` serialization with jsons.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		super().setUp()
		
		self.circuitJsonDict = {
			'description': None,
			'grouping': 1,
			'length': 10.0,
			'loadType': 'POWER',
			'name': 'Test Circuit',
			'phases': 1,
			'power': 5000.0,
			'referenceMethod': 'B1',
			'temperature': 30,
			'voltage': 100,
			'wireConfiguration': 'TWO',
			'wireType': {
				'insulation': 'PVC',
				'material': 'COPPER'
			},
		}
	
	
	def testSerializeCircuit( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		circuitJsonDict = dump( self.circuit, strip_properties = True )
		self.assertEqual( circuitJsonDict, self.circuitJsonDict )
	
	
	def testDeserializeCircuit( self ) -> None:
		'''
		Test deserialization with jsons.load.
		'''
		
		circuit = load( self.circuitJsonDict, Circuit )
		self.assertEqual( circuit, self.circuit )