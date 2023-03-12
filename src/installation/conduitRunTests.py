# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase

from .conduitRun import ConduitRun



class BaseConduitRunTests( TestCase ):
	'''
	Base class for all `ConduitRun` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.conduitRun = ConduitRun(
			name = 'Test Conduit Run',
			diameter = 10.0,
			length = 10.0,
		)



class ConduitRunBasicTests( BaseConduitRunTests ):
	'''
	Basic tests for `ConduitRun` class.
	'''



class ConduitRunSerializationTests( BaseConduitRunTests ):
	'''
	Tests for `ConduitRun` serialization with jsons.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		super().setUp()
		
		self.conduitRunJsonDict = {
			'name': 'Test Conduit Run',
			'diameter': 10.0,
			'length': 10.0,
		}
	
	
	def testSerializeConduitRun( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		self.assertEqual( self.conduitRun.dump(), self.conduitRunJsonDict )
	
	
	def testDeserializeConduitRun( self ) -> None:
		'''
		Test deserialization with jsons.load.
		'''
		
		self.assertEqual( ConduitRun.load( self.conduitRunJsonDict ), self.conduitRun )