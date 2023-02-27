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



class ProjectTests( TestCase ):
	'''
	Tests for `Project` class.
	'''
	
	def testEmptyProject( self ) -> None:
		'''
		Test empty `Project`.
		'''
		
		Project( 'Test Project', [] )
	
	
	def testProjectWithCircuits( self ) -> None:
		'''
		Test `Project` with `Circuit`s.
		'''
		
		wireType = WireType( WireMaterial.COPPER, WireInsulation.PVC )
		circuit = Circuit(
			name				= 'Test Circuit',
			loadType			= LoadType.POWER,
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
		
		Project( 'Test Project', [ circuit ] )