# 
# NBR 5410 Calculator
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



from enum import Enum

from PySide6.QtCore import (
	Qt,
	QAbstractItemModel,
	QPersistentModelIndex,
	Slot,
)
from PySide6.QtWidgets import (
	QWidget,
	QAbstractItemView,
	QListView,
	QTreeView,
	QStyledItemDelegate,
	QStyleOptionViewItem,
	QComboBox,
)
from PySide6.QtGui import QDrag

from .models import ModelIndex



class GenericListView( QListView ):
	'''
	`QListView` for `GenericItemModel`.
	'''
	
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
	
	
	@Slot()
	def newItem( self ) -> None:
		'''
		Insert new item at end of table.
		'''
		
		itemCount = self.model().rowCount()
		self.model().insertRow( itemCount )
	
	
	@Slot()
	def deleteSelectedItems( self ) -> None:
		'''
		Delete selected items from table.
		'''
		
		indexes = {
			QPersistentModelIndex( index )
			for index in self.selectedIndexes()
			if index.column() == 0
		}
		
		for index in indexes:
			self.model().removeRow( index.row() )



class GenericTreeView( QTreeView ):
	'''
	`QTreeView` for `GenericItemModel`.
	'''
	
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		
		self.setItemDelegate( EnumDelegate( self ) )
		
		self.setUniformRowHeights( True )
		self.setAllColumnsShowFocus( True )
		self.setAlternatingRowColors( True )
		self.setAnimated( True )
		
		self.setSelectionMode( QAbstractItemView.SelectionMode.ExtendedSelection )
		self.setDragDropMode( QAbstractItemView.DragDropMode.InternalMove )
		self.setSortingEnabled( True )
	
	
	def resizeColumnsToContents( self ) -> None:
		'''
		Resizes all columns given the size of their contents.
		'''
		
		for index in range( self.model().columnCount() ):
			self.resizeColumnToContents( index )
	
	
	def startDrag( self, supportedActions: Qt.DropAction ) -> None:
		'''
		Starts a drag by calling drag.exec() using the given supportedActions.
		'''
		
		indexes = [
			index
			for index in self.selectedIndexes()
			if Qt.ItemFlag.ItemIsDragEnabled in self.model().flags( index )
		]
		
		if not indexes:
			return
		
		data = self.model().mimeData( indexes )
		
		drag = QDrag( self )
		drag.setMimeData( data )
		drag.exec( supportedActions )
	
	
	@Slot()
	def newItem( self ) -> None:
		'''
		Insert new item at end of table.
		'''
		
		itemCount = self.model().rowCount()
		self.model().insertRow( itemCount )
	
	
	@Slot()
	def deleteSelectedItems( self ) -> None:
		'''
		Delete selected items from table.
		'''
		
		indexes = {
			QPersistentModelIndex( index )
			for index in self.selectedIndexes()
			if index.column() == 0
		}
		
		for index in indexes:
			self.model().removeRow( index.row() )



class EnumDelegate( QStyledItemDelegate ):
	'''
	`QStyledItemDelegate` with support for displaying and editing `Enum`s.
	'''
	
	def createEditor(
		self,
		parent: QWidget,
		option: QStyleOptionViewItem,
		index: ModelIndex
	) -> QWidget:
		'''
		Returns the editor to be used for editing the data item with the given `index`.
		'''
		
		match value := index.model().data( index, Qt.ItemDataRole.EditRole ):
			case Enum():
				editor = QComboBox( parent )
				
				for enumItem in type( value ):
					editor.addItem( enumItem.name, enumItem )
				
				return editor
			
			case _:
				return super().createEditor( parent, option, index )
	
	
	def setEditorData( self, editor: QWidget, index: ModelIndex ) -> None:
		'''
		Sets the contents of the given `editor` to the data for the item at the given `index`.
		'''
		
		match value := index.model().data( index, Qt.ItemDataRole.EditRole ), editor:
			case Enum(), QComboBox() as enumEditor:
				enumEditor.setCurrentText( value.name )
			
			case _:
				super().setEditorData( editor, index )
	
	
	def setModelData( self, editor: QWidget, model: QAbstractItemModel, index: ModelIndex ) -> None:
		'''
		Sets the data for the item at the given `index` in the model to the contents of the given
		`editor`.
		'''
		
		match index.model().data( index, Qt.ItemDataRole.EditRole ), editor:
			case Enum(), QComboBox() as enumEditor:
				model.setData( index, enumEditor.currentData(), Qt.ItemDataRole.EditRole )
			
			case _:
				super().setModelData( editor, model, index )