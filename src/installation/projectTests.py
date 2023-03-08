# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from unittest import TestCase

from .project import Project
from .circuit import (
	LoadType,
	WireMaterial,
	WireInsulation,
	WireType,
	ReferenceMethod,
	WireConfiguration,
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
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		circuit = Circuit(
			name				= 'Test Circuit',
			loadType			= loadType,
			voltage				= 100,
			phases				= 1,
			grouping			= 1,
			length				= 10.0,
			referenceMethod		= ReferenceMethod.B1,
			wireConfiguration	= WireConfiguration.TWO,
			wireType			= wireType,
			temperature			= 30,
			power				= 5000,
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