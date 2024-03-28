# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase
from typing import Any
from dataclasses import dataclass
from uuid import UUID

from typing_extensions import Self

from nbr_5410_calculator.installation.util import UniqueSerializable



class TestClass( UniqueSerializable ):
	'''
	Regular sub-class of `uniqueSerializable`.
	'''
	
	def __init__( self, name: str, **kwargs: Any ) -> None:
		super().__init__( **kwargs )
		
		self.name = name
	
	
	def __eq__( self, other: Self ) -> bool:
		return self.name == other.name and self.uuid == other.uuid



@dataclass
class TestDataclass( UniqueSerializable ):
	'''
	Dataclass sub-class of `uniqueSerializable`.
	'''
	
	name: str



@dataclass
class TestContainerDataclass( UniqueSerializable ):
	'''
	Nested sub-class of `uniqueSerializable`.
	'''
	
	items: list[TestDataclass]



class BaseUniqueSerializableTests( TestCase ):
	'''
	Base class for all `uniqueSerializable` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		UniqueSerializable._instances = {}
		
		self.testClass = TestClass(
			name = 'Test Instance',
			uuid = UUID( 'e3f9a216-774e-46ee-986a-190abdb37b32' ),
		)
		
		self.testDataclass = TestDataclass(
			name = 'Test Instance',
			uuid = UUID( 'e3f9a216-774e-46ee-986a-190abdb37b32' ),
		)
		
		self.testClassJsonDict = {
			'name': 'Test Instance',
			'uuid': 'e3f9a216-774e-46ee-986a-190abdb37b32',
		}



class UniqueSerializableClassSerializationTests( BaseUniqueSerializableTests ):
	'''
	Test serialization of regular sub-class of `uniqueSerializable`.
	'''
	
	def testSerialize( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		self.assertEqual( self.testClass.dump(), self.testClassJsonDict )
	
	
	# TODO
	# def testDeserialize( self ) -> None:
	# 	'''
	# 	Test deserialization with jsons.load.
	# 	'''
		
	# 	self.assertEqual( TestClass.load( self.testClassJsonDict ), self.testClass )
	
	
	def testDeserializeWithoutUuid( self ) -> None:
		'''
		Test deserialization without UUID.
		'''
		
		self.testClassJsonDict.pop( 'uuid' )
		testClass = TestClass.load( self.testClassJsonDict )
		self.testClass.uuid = testClass.uuid
		
		self.assertIsNotNone( testClass.uuid )
		self.assertEqual( testClass, self.testClass )
	
	
	# TODO
	# def testDeserializeDuplicated( self ) -> None:
	# 	'''
	# 	Test deserialization of two items with the same UUID.
	# 	'''
		
	# 	testClass1 = TestClass.load( self.testClassJsonDict )
	# 	testClass2 = TestClass.load( self.testClassJsonDict )
		
	# 	self.assertIs( testClass1, testClass2 )



class UniqueSerializableDataclassSerializationTests( BaseUniqueSerializableTests ):
	'''
	Test serialization of dataclass sub-class of `uniqueSerializable`.
	'''
	
	def testSerialize( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		self.assertEqual( self.testDataclass.dump(), self.testClassJsonDict )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization with jsons.load.
		'''
		
		self.assertEqual( TestDataclass.load( self.testClassJsonDict ), self.testDataclass )
	
	
	def testDeserializeWithoutUuid( self ) -> None:
		'''
		Test deserialization without UUID.
		'''
		
		self.testClassJsonDict.pop( 'uuid' )
		testDataclass = TestDataclass.load( self.testClassJsonDict )
		self.testDataclass.uuid = testDataclass.uuid
		
		self.assertIsNotNone( testDataclass.uuid )
		self.assertEqual( testDataclass, self.testDataclass )
	
	
	def testDeserializeDuplicated( self ) -> None:
		'''
		Test deserialization of two items with the same UUID.
		'''
		
		testClass1 = TestDataclass.load( self.testClassJsonDict )
		testClass2 = TestDataclass.load( self.testClassJsonDict )
		
		self.assertIs( testClass1, testClass2 )



class NestedUniqueSerializableSerializationTests( BaseUniqueSerializableTests ):
	'''
	Test serialization of nested sub-class of `uniqueSerializable`.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		super().setUp()
		
		self.testContainerDataclass = TestContainerDataclass(
			items = [ self.testDataclass, self.testDataclass ],
			uuid = UUID( 'd5c04a14-7e60-4b18-bf8b-97b34eaa33a2' ),
		)
		
		self.testContainerDataclassJsonDict = {
			'items': [ self.testClassJsonDict, self.testClassJsonDict ],
			'uuid': 'd5c04a14-7e60-4b18-bf8b-97b34eaa33a2',
		}
	
	
	def testSerialize( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		self.assertEqual( self.testContainerDataclass.dump(), self.testContainerDataclassJsonDict )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization with jsons.load.
		'''
		
		testContainerDataclass = TestContainerDataclass.load( self.testContainerDataclassJsonDict )
		
		self.assertEqual( testContainerDataclass, self.testContainerDataclass )
		self.assertIs( testContainerDataclass.items[0], testContainerDataclass.items[1] )