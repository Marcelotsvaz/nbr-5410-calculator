# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from typing import override
from unittest import TestCase

from nbr_5410_calculator.installation.project import Project
from nbr_5410_calculator.installation.util import UniqueSerializable
from tests.installation.circuit_tests import createCircuitDict
from tests.installation.util import createProject, createProjectDict



class BaseProjectTests( TestCase ):
	'''
	Base class for all `Project` tests.
	'''
	
	@override
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		UniqueSerializable.clearInstanceRegistry()
		
		self.project = createProject()
		self.projectDict = createProjectDict( [ createCircuitDict() ] * 3 )



class ProjectTests( BaseProjectTests ):
	'''
	Tests for `Project` class.
	'''
	
	def testEmptyProject( self ) -> None:
		'''
		Test empty `Project`.
		'''
		
		Project( name = 'Test Project' )



class ProjectSerializationTests( BaseProjectTests ):
	'''
	Tests for `Project` serialization with Pydantic.
	'''
	
	def testSerialize( self ) -> None:
		'''
		Test serialization.
		'''
		
		self.assertEqual( self.project.model_dump(), self.projectDict )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		self.assertEqual( Project.model_validate( self.projectDict ), self.project )