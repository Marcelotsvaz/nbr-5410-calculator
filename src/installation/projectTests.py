# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase
from uuid import UUID
from typing import Any

from .project import Project
from .circuitTests import createCircuit, createCircuitJsonDict
from .conduitRunTests import createConduitRun, createConduitRunJsonDict



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
		'name': 'Test Project',
		'uuid': 'd1019f95-f48d-4a66-b1c3-681c802d396a',
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
		
		Project( 'Test Project' )



class ProjectSerializationTests( BaseProjectTests ):
	'''
	Tests for `Project` serialization with jsons.
	'''
	
	def testSerialize( self ) -> None:
		'''
		Test serialization with jsons.dump.
		'''
		
		self.assertEqual( self.project.dump(), createProjectJsonDict() )
	
	
	def testDeserialize( self ) -> None:
		'''
		Test deserialization with jsons.load.
		'''
		
		projectJsonDict = createProjectJsonDict()
		for circuitJsonDict in projectJsonDict['circuits']:
			circuitJsonDict['-meta'] = {
				'classes': { '/': 'installation.circuit.Circuit' }
			}
		
		self.assertEqual( Project.load( projectJsonDict ), self.project )