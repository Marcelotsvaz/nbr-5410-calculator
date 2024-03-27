'''
PDM backend plugins.
'''

from pathlib import Path

from pdm.backend.hooks import Context



class Hooks:
	'''
	PDM backend hooks.
	'''
	
	def pdm_build_clean( self, context: Context ) -> None:	# pylint: disable = invalid-name
		'''
		Change default build directory before start of build.
		'''
		
		context.build_dir = Path( '.staging/build/' ).resolve()