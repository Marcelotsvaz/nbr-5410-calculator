# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase
from uuid import UUID
from typing import Any

from .conduitRun import ConduitRun



def createConduitRun() -> ConduitRun:
	'''
	Create instance of `ConduitRun`.
	'''
	
	conduitRun = ConduitRun(
		diameter = 10.0,
		id = UUID( 'e3f9a216-774e-46ee-986a-190abdb37b32' ),
		length = 10.0,
		name = 'Test Conduit Run',
	)
	
	return conduitRun



def createConduitRunJsonDict() -> dict[str, Any]:
	'''
	Create JSON dict for `ConduitRun`.
	'''
	
	conduitRunJsonDict = {
		'diameter': 10.0,
		'id': 'e3f9a216-774e-46ee-986a-190abdb37b32',
		'length': 10.0,
		'name': 'Test Conduit Run',
	}
	
	return conduitRunJsonDict



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
		
		self.assertEqual( ConduitRun.load( createConduitRunJsonDict() ), self.conduitRun )