# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase

from .project import Project
from .circuit import (
	Supply,
	LoadType,
	WireMaterial,
	WireInsulation,
	WireType,
	ReferenceMethod,
	Circuit,
)
from .conduitRun import ConduitRun



class ProjectTests( TestCase ):
	'''
	Tests for `Project` class.
	'''
	
	def testEmptyProject( self ) -> None:
		'''
		Test empty `Project`.
		'''
		
		Project( 'Test Project' )
	
	
	def testProjectWithCircuits( self ) -> None:
		'''
		Test `Project` with `Circuit`s.
		'''
		
		loadType = LoadType( 'Power', 2.5, 1.0 )
		supply = Supply( 100, 1 )
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		circuit = Circuit(
			grouping		= 1,
			length			= 10.0,
			loadType		= loadType,
			name			= 'Test Circuit',
			loadPower		= 5000,
			referenceMethod	= ReferenceMethod.B1,
			supply			= supply,
			temperature		= 30,
			wireType		= wireType,
		)
		
		Project( 'Test Project', circuits = [ circuit ] )
	
	
	def testProjectWithConduitRuns( self ) -> None:
		'''
		Test `Project` with `ConduitRun`s.
		'''
		
		conduitRun = ConduitRun(
			name = 'Test Conduit Run',
			diameter = 10.0,
			length = 10.0,
		)
		
		Project( 'Test Project', conduitRuns = [ conduitRun ] )