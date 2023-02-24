# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase

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
)



class CircuitTests( TestCase ):
	'''
	Tests for `Circuit` class.
	'''
	
	def setUp( self ) -> None:
		'''
		Base fixture for all `Circuit` tests.
		'''
		
		self.wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		
		self.circuit = Circuit(
			name				= 'circuit',
			loadType			= LoadType.POWER,
			voltage				= 100,
			phases				= 1,
			grouping			= 1,
			length				= 10.0,
			referenceMethod		= ReferenceMethod.B1,
			wireConfiguration	= WireConfiguration.TWO,
			wireType			= self.wireType,
			temperature			= 30,
			power				= 5000.0,
		)
		
		return super().setUp()
	
	
	def testCurrent( self ) -> None:
		'''
		Test `current` property.
		'''
		
		self.assertEqual( self.circuit.current, 50.0 )
	
	
	def testProjectCurrent( self ) -> None:
		'''
		Test `projectCurrent` property.
		'''
		
		self.assertEqual( self.circuit.projectCurrent, 50.0 )
	
	
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
		
		self.assertAlmostEqual( self.circuit.projectCurrent, 81.967213, 6 )
	
	
	def testTemperatureCorrectionInterpolation( self ) -> None:
		'''
		Test temperature correction with interpolated value.
		'''
		
		self.circuit.temperature = 58
		
		self.assertAlmostEqual( self.circuit.projectCurrent, 91.911765, 6 )
	
	
	def testTemperatureCorrectionBelowMinimum( self ) -> None:
		'''
		Temperatures below minimum should use the factor for the lowest temperature available.
		'''
		
		self.circuit.temperature = -10
		
		self.assertAlmostEqual( self.circuit.projectCurrent, 40.983607, 6 )
	
	
	def testTemperatureCorrectionAboveMaximum( self ) -> None:
		'''
		Temperatures above maximum for the given insulation type should raise an exeception.
		'''
		
		self.circuit.temperature = 70
		
		with self.assertRaises( Exception ):
			_ = self.circuit.projectCurrent