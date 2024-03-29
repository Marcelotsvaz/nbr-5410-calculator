# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase
from uuid import UUID
from typing import Any

from .conduitRun import ConduitType, Conduit, ConduitRun
from .circuitTests import createCircuit, createCircuitJsonDict



def createConduitRun() -> ConduitRun:
	'''
	Create instance of `ConduitRun`.
	'''
	
	conduitRun = ConduitRun(
		circuits = [ createCircuit(), createCircuit(), createCircuit() ],
		length = 10.0,
		name = 'Test Conduit Run',
		uuid = UUID( 'f4f3bd7c-c818-4ffc-a776-212469d8ba16' ),
	)
	
	return conduitRun



def createConduitRunJsonDict() -> dict[str, Any]:
	'''
	Create JSON dict for `ConduitRun`.
	'''
	
	conduitRunJsonDict = {
		'circuits': [ createCircuitJsonDict() ] * 3,
		'length': 10.0,
		'name': 'Test Conduit Run',
		'uuid': 'f4f3bd7c-c818-4ffc-a776-212469d8ba16',
	}
	
	return conduitRunJsonDict



class ConduitTests( TestCase ):
	'''
	Basic tests for `Conduit` class.
	'''
	
	def testSection( self ) -> None:
		'''
		Test `Conduit.section`.
		'''
		
		conduit = Conduit( ConduitType.RIGID, '25 mm', 23.0, 25.0 )
		
		self.assertAlmostEqual( conduit.section, 490.873852, 6 )



class BaseConduitRunTests( TestCase ):
	'''
	Base class for all `ConduitRun` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.conduitRun = createConduitRun()



class ConduitRunBasicTests( BaseConduitRunTests ):
	'''
	Basic tests for `ConduitRun` class.
	'''
	
	def testFilledSection( self ) -> None:
		'''
		Test `ConduitRun.filledSection`.
		'''
		
		self.assertAlmostEqual( self.conduitRun.filledSection, 246.057391, 6 )
	
	
	def testFilledSectionFewWires( self ) -> None:
		'''
		Test `ConduitRun.filledSection` when conduit has less than 3 wires.
		'''
		
		circuit = createCircuit()
		circuit.supply.hasGround = False
		self.conduitRun.circuits = [ circuit ]
		
		self.assertAlmostEqual( self.conduitRun.filledSection, 54.679420, 6 )
	
	
	def testFillFactor( self ) -> None:
		'''
		Test `ConduitRun.fillFactor`.
		'''
		
		self.assertAlmostEqual( self.conduitRun.fillFactor, 0.240399, 6 )
	
	
	def testFillFactorFewWires( self ) -> None:
		'''
		Test `ConduitRun.fillFactor` when conduit has less than 3 wires.
		'''
		
		circuit = createCircuit()
		circuit.supply.hasGround = False
		self.conduitRun.circuits = [ circuit ]
		
		self.assertAlmostEqual( self.conduitRun.fillFactor, 0.258849, 6 )



class ConduitRunSerializationTests( BaseConduitRunTests ):
	'''
	Tests for `ConduitRun` serialization with jsons.
	'''
	
	def testSerialize( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		self.assertEqual( self.conduitRun.dump(), createConduitRunJsonDict() )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization with jsons.load.
		'''
		
		# FIXME
		conduitRunJsonDict = createConduitRunJsonDict()
		for circuitJsonDict in conduitRunJsonDict['circuits']:
			circuitJsonDict['-meta'] = {
				'classes': { '/': 'installation.circuit.Circuit' }
			}
		
		self.assertEqual( ConduitRun.load( conduitRunJsonDict ), self.conduitRun )