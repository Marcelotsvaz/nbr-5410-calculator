# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase
from uuid import UUID
from typing import Any

from nbr_5410_calculator.installation.project import Project
from tests.installation.circuit_tests import createCircuit, createCircuitJsonDict
from tests.installation.conduit_run_tests import createConduitRun, createConduitRunJsonDict



def createProject() -> Project:
	'''
	Create instance of `Project`.
	'''
	
	project = Project(
		circuits = [ createCircuit(), createCircuit(), createCircuit() ],
		conduitRuns = [ createConduitRun(), createConduitRun(), createConduitRun() ],
		name = 'Test Project',
		uuid = UUID( 'd1019f95-f48d-4a66-b1c3-681c802d396a' ),
	)
	
	return project



def createProjectJsonDict() -> dict[str, Any]:
	'''
	Create JSON dict for `Project`.
	'''
	
	projectJsonDict = {
		'circuits': [ createCircuitJsonDict() ] * 3,
		'conduitRuns': [ createConduitRunJsonDict() ] * 3,
		'loadTypes': [],
		'name': 'Test Project',
		'supplies': [],
		'uuid': UUID( 'd1019f95-f48d-4a66-b1c3-681c802d396a' ),
		'wireTypes': [],
	}
	
	return projectJsonDict



class BaseProjectTests( TestCase ):
	'''
	Base class for all `Project` tests.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.project = createProject()



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
	
	# TODO: Pydantic handle base class
	def testSerialize( self ) -> None:
		'''
		Test serialization.
		'''
		
		self.assertEqual( self.project.model_dump(), createProjectJsonDict() )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization.
		'''
		
		self.assertEqual( Project.model_validate( createProjectJsonDict() ), self.project )