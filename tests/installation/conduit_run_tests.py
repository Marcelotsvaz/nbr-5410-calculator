# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase

from nbr_5410_calculator.installation.circuit import ProjectError
from nbr_5410_calculator.installation.conduitRun import (
	Conduit,
	ConduitRun,
	ConduitType,
)
from tests.installation.util import (
	createCircuit,
	createCircuitDict,
	createConduitRun,
	createConduitRunDict,
)



class ConduitTests( TestCase ):
	'''
	Basic tests for `Conduit` class.
	'''
	
	def testSection( self ) -> None:
		'''
		Test `Conduit.section`.
		'''
		
		conduit = Conduit(
			conduitType = ConduitType.RIGID,
			nominalDiameter = '25 mm',
			externalDiameter = 25.0,
			internalDiameter = 23.0,
		)
		
		self.assertAlmostEqual( conduit.section, 415.475628, 6 )



class BaseConduitRunTests( TestCase ):
	'''
	Base class for all `ConduitRun` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.conduitRun = createConduitRun()
		self.conduitRun.circuits = [ createCircuit( self.conduitRun ) ] * 3
		
		self.conduitRunDict = createConduitRunDict( [ createCircuitDict() ] * 3 )



class ConduitRunBasicTests( BaseConduitRunTests ):
	'''
	Basic tests for `ConduitRun` class.
	'''
	
	def testFilledSection( self ) -> None:
		'''
		Test `ConduitRun.filledSection`.
		'''
		
		self.assertAlmostEqual( self.conduitRun.filledSection, 346.360590, 6 )
	
	
	def testFillFactor( self ) -> None:
		'''
		Test `ConduitRun.fillFactor`.
		'''
		
		self.assertAlmostEqual( self.conduitRun.fillFactor, 0.338395, 6 )
	
	
	def testFilledSectionFewWires( self ) -> None:
		'''
		Test `ConduitRun.filledSection` when conduit has less than 3 wires.
		'''
		
		self.conduitRun.circuits = self.conduitRun.circuits[:1]
		self.conduitRun.circuits[0].supply.hasGround = False
		
		self.assertAlmostEqual( self.conduitRun.filledSection, 54.679420, 6 )
	
	
	def testFillFactorFewWires( self ) -> None:
		'''
		Test `ConduitRun.fillFactor` when conduit has less than 3 wires.
		'''
		
		self.conduitRun.circuits = self.conduitRun.circuits[:1]
		self.conduitRun.circuits[0].supply.hasGround = False
		
		self.assertAlmostEqual( self.conduitRun.fillFactor, 0.258849, 6 )



class ConduitRunCorrectionFactorTests( BaseConduitRunTests ):
	'''
	Test `ConduitRun` correction factor by temperature and grouping.
	'''
	
	def testGroupingFactor( self ) -> None:
		'''
		Test grouping factor.
		'''
		
		self.assertEqual( self.conduitRun.correctionFactor, 0.70 )
	
	
	def testTemperatureCorrection( self ) -> None:
		'''
		Test temperature correction with round value.
		'''
		
		self.conduitRun.temperature = 55
		
		self.assertEqual( self.conduitRun.correctionFactor, 0.427 )
	
	
	def testTemperatureCorrectionInterpolation( self ) -> None:
		'''
		Test temperature correction with interpolated value.
		'''
		
		self.conduitRun.temperature = 58
		
		self.assertEqual( self.conduitRun.correctionFactor, 0.3808 )
	
	
	def testTemperatureCorrectionBelowMinimum( self ) -> None:
		'''
		Temperatures below minimum should use the factor for the lowest temperature available.
		'''
		
		self.conduitRun.temperature = -10
		
		self.assertEqual( self.conduitRun.correctionFactor, 0.854 )
	
	
	def testTemperatureCorrectionAboveMaximum( self ) -> None:
		'''
		Temperatures above maximum for the given insulation type should raise an exception.
		'''
		
		self.conduitRun.temperature = 70
		
		with self.assertRaises( ProjectError ):
			_ = self.conduitRun.correctionFactor



class ConduitRunSerializationTests( BaseConduitRunTests ):
	'''
	Tests for `ConduitRun` serialization with Pydantic.
	'''
	
	# TODO: Pydantic handle base class
	def testSerialize( self ) -> None:
		'''
		Test serialization.
		'''
		
		self.assertEqual( self.conduitRun.model_dump(), self.conduitRunDict )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		self.assertEqual( ConduitRun.model_validate( self.conduitRunDict ), self.conduitRun )