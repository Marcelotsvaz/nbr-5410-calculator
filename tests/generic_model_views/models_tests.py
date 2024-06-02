'''
Tests for `nbr_5410_calculator.generic_model_views.models`.
'''

from unittest import TestCase

from PySide6.QtCore import QModelIndex

from nbr_5410_calculator.generic_model_views.models import GenericItem, GenericItemModel, RootItem



class GenericItemModelIndexTests( TestCase ):
	'''
	Tests for `index` and `parent` methods of `GenericItemModelTests`.
	'''
	
	def setUp( self ) -> None:
		'''
		Setup for all tests.
		'''
		
		self.model = GenericItemModel[GenericItem](
			datasource = [],
			dataType = GenericItem,
		)
	
	
	def testRootIndex( self ) -> None:
		'''
		Index (0, 0, (-1, -1)) should point to root item.
		'''
		
		self.assertEqual(
			self.model.index( 0, 0 ),
			self.model.createIndex( 0, 0, self.model.root ),
		)
	
	
	def testRootIndexColumns( self ) -> None:
		'''
		Root item can have as many rows as the rest of the model.
		'''
		
		self.assertEqual(
			self.model.index( 0, 5 ), 
			self.model.createIndex( 0, 5, self.model.root ),
		)
	
	
	def testRootIndexInvalidRow( self ) -> None:
		'''
		Root item has no siblings.
		'''
		
		with self.assertRaises( LookupError ):
			self.model.index( 1, 0 )
	
	
	def testRootIndexParent( self ) -> None:
		'''
		Root index has no parent.
		'''
		
		rootIndex = self.model.index( 0, 0 )
		
		self.assertEqual( self.model.parent( rootIndex ), QModelIndex() )
	
	
	def testRootIndexParentColumns( self ) -> None:
		'''
		Root index has no parent.
		Root item can have as many rows as the rest of the model.
		'''
		
		rootIndex = self.model.index( 0, 5 )
		
		self.assertEqual( self.model.parent( rootIndex ), QModelIndex() )
	
	
	def testTopLevelIndexParent( self ) -> None:
		'''
		Top-level items should be children of the root item.
		'''
		
		self.model.root.children.append( GenericItem() )
		
		rootIndex = self.model.index( 0, 0 )
		index = self.model.index( 0, 0, rootIndex )
		
		self.assertEqual( self.model.parent( index ), rootIndex )
	
	
	def testTopLevelIndexParentColumns( self ) -> None:
		'''
		By convention only the first column can have children.
		'''
		
		self.model.root.children.append( GenericItem() )
		
		rootIndex = self.model.index( 0, 0 )
		index = self.model.index( 0, 5, rootIndex )
		
		self.assertEqual( self.model.parent( index ), rootIndex )
	
	
	def testNestedIndexParent( self ) -> None:
		'''
		Test children of top-level index.
		'''
		
		container = RootItem( items = [
			GenericItem(),
			GenericItem(),
			GenericItem(),
		] )
		
		self.model.root.children.append( container )
		
		rootIndex = self.model.index( 0, 0 )
		parentIndex = self.model.index( 0, 0, rootIndex )
		childIndex = self.model.index( 0, 0, parentIndex )
		
		self.assertEqual( self.model.parent( childIndex ), parentIndex )