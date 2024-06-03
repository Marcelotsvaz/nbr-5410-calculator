# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase
from uuid import UUID

from nbr_5410_calculator.installation.util import UniqueSerializable



class TestClass( UniqueSerializable ):
	'''
	Regular sub-class of `uniqueSerializable`.
	'''
	
	name: str



class TestContainerClass( UniqueSerializable ):
	'''
	Nested sub-class of `uniqueSerializable`.
	'''
	
	items: list[TestClass]



class BaseUniqueSerializableTests( TestCase ):
	'''
	Base class for all `uniqueSerializable` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.testClass = TestClass(
			name = 'Test Instance',
			uuid = UUID( 'e3f9a216-774e-46ee-986a-190abdb37b32' ),
		)
		
		self.testClassJsonDict = {
			'name': 'Test Instance',
			'uuid': 'e3f9a216-774e-46ee-986a-190abdb37b32',
		}



class UniqueSerializableTests( BaseUniqueSerializableTests ):
	'''
	Test serialization of regular sub-class of `uniqueSerializable`.
	'''
	
	def testSerialize( self ) -> None:
		'''
		Test serialization.
		'''
		
		self.assertEqual( self.testClass.model_dump(), self.testClassJsonDict )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		self.assertEqual( TestClass.model_validate( self.testClassJsonDict ), self.testClass )
	
	
	def testDeserializeWithoutUuid( self ) -> None:
		'''
		Test deserialization without UUID.
		'''
		
		self.testClassJsonDict.pop( 'uuid' )
		testClass = TestClass.model_validate( self.testClassJsonDict )
		self.testClass.uuid = testClass.uuid
		
		self.assertIsNotNone( testClass.uuid )
		self.assertEqual( testClass, self.testClass )
	
	
	def testDeserializeDuplicated( self ) -> None:
		'''
		Test deserialization of two items with the same UUID.
		'''
		
		context: dict[str, TestClass] = {}
		
		testClass1 = TestClass.model_validate( self.testClassJsonDict, context = context )
		testClass2 = TestClass.model_validate( self.testClassJsonDict, context = context )
		
		self.assertIs( testClass1, testClass2 )



class NestedUniqueSerializableTests( BaseUniqueSerializableTests ):
	'''
	Test serialization of nested sub-class of `uniqueSerializable`.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		super().setUp()
		
		self.testContainerClass = TestContainerClass(
			items = [ self.testClass, self.testClass ],
			uuid = UUID( 'd5c04a14-7e60-4b18-bf8b-97b34eaa33a2' ),
		)
		
		self.testContainerJsonDict = {
			'items': [ self.testClassJsonDict, self.testClassJsonDict ],
			'uuid': 'd5c04a14-7e60-4b18-bf8b-97b34eaa33a2',
		}
	
	
	def testSerialize( self ) -> None:
		'''
		Test serialization.
		'''
		
		self.assertEqual( self.testContainerClass.model_dump(), self.testContainerJsonDict )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		testContainerClass = TestContainerClass.model_validate( self.testContainerJsonDict, context = {} )
		
		self.assertEqual( testContainerClass, self.testContainerClass )
		self.assertIs( testContainerClass.items[0], testContainerClass.items[1] )