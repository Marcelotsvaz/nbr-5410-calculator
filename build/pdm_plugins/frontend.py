'''
PDM frontend plugins.
'''

from argparse import ArgumentParser, Namespace

from pdm.cli.commands import build, publish
from pdm.core import Core
from pdm.project import Project



def customDirs( core: Core ) -> None:
	'''
	Change `build` and `dist` directories.
	'''
	
	core.register_command( BuildCommand )
	core.register_command( PublishCommand )



class BuildCommand( build.Command ):
	'''
	Build artifacts for distribution
	'''
	
	name = 'build'
	
	
	def add_arguments( self, parser: ArgumentParser ) -> None:
		super().add_arguments( parser )
		
		for action in parser._actions:	# pylint: disable = protected-access
			if action.dest == 'dest':
				action.default = '.staging/dist'
				break



class PublishCommand( publish.Command ):
	'''
	Build and publish the project to PyPI
	'''
	
	name = 'publish'
	
	
	def handle( self, project: Project, options: Namespace ) -> None:
		if options.build:
			BuildCommand.do_build( project, dest = '.staging/dist' )
		
		options.build = False
		
		realProjectRoot = project.root
		project.root = realProjectRoot.joinpath( '.staging' )
		super().handle( project, options )
		project.root = realProjectRoot