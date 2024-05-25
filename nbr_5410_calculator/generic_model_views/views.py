'''

'''

from enum import Enum
from typing import override

from PySide6 import QtGui
from PySide6.QtCore import (
	QAbstractItemModel,
	QModelIndex,
	QPersistentModelIndex,
	QPoint,
	QRect,
	Qt,
	Slot,
)
from PySide6.QtWidgets import (
	QAbstractItemView,
	QComboBox,
	QListView,
	QStyle,
	QStyledItemDelegate,
	QStyleOption,
	QStyleOptionViewItem,
	QTreeView,
	QWidget,
)
from PySide6.QtGui import QDrag, QPainter, QPixmap

from .models import ModelIndex



class GenericListView( QListView ):
	'''
	`QListView` for `GenericItemModel`.
	'''
	
	@override
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
	
	
	@Slot()
	def newItem( self ) -> None:
		'''
		Insert new item.
		'''
		
		# After last item.
		self.model().insertRow( self.model().rowCount() + 1 )
	
	
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
	
	@override
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		
		self.dropIndicatorRect = QRect()
		
		# self.setItemDelegate( EnumDelegate( self ) ) # TODO: Proper delegate.
		
		self.setUniformRowHeights( True )
		self.setAllColumnsShowFocus( True )
		self.setAlternatingRowColors( True )
		self.setAnimated( True )
		
		self.setSelectionMode( QAbstractItemView.SelectionMode.ExtendedSelection )
		self.setDragDropMode( QAbstractItemView.DragDropMode.InternalMove )
		self.setDefaultDropAction( Qt.DropAction.MoveAction )
		# self.setSortingEnabled( True )
	
	
	def resizeColumnsToContents( self ) -> None:
		'''
		Resizes all columns given the size of their contents.
		'''
		
		for index in range( self.model().columnCount() ):
			self.resizeColumnToContents( index )
	
	
	def selectedRowIndexes( self ) -> list[QModelIndex]:
		'''
		Return a sorted list of indexes, one for each selected row.
		'''
		
		return [
			index
			for index in sorted( self.selectedIndexes(), key = lambda index: index.row() )
			if index.column() == 0
		]
	
	
	@override
	def startDrag( self, supportedActions: Qt.DropAction ) -> None:
		'''
		Starts a drag by calling `drag.exec()` using the given `supportedActions`.
		
		Delete items moved to outside the view.
		'''
		
		# Get selected draggable indexes.
		selectedIndexes = [
			index
			for index in self.selectedRowIndexes()
			if Qt.ItemFlag.ItemIsDragEnabled in self.model().flags( index )
		]
		
		if not selectedIndexes:
			return
		
		# Set up drag with model's MIME data.
		drag = QDrag( self )
		data = self.model().mimeData( selectedIndexes )
		drag.setMimeData( data )
		
		# Set drag pixmap.
		pixmap = QPixmap( 100, 5 )
		pixmap.fill( 'white' )
		drag.setPixmap( pixmap )
		drag.setHotSpot( pixmap.rect().center() )
		
		# Execute drag.
		action = drag.exec( supportedActions, self.defaultDropAction() )
		
		# Delete moved items.
		if action is Qt.DropAction.MoveAction and drag.target() and drag.target() not in self.children():
			for index in [ QPersistentModelIndex( index ) for index in selectedIndexes ]:
				self.model().removeRow( index.row(), index.parent() )
	
	
	def dropTargetForPosition( self, position: QPoint ) -> tuple[int, QModelIndex, QRect]:
		'''
		Calculate drop index and drop indicator based on vertical position.
		'''
		
		index = self.indexAt( position )
		
		# Dropped on viewport.
		if not index.isValid():
			index = self.model().index( self.model().rowCount() - 1, 0 )
		
		parent = index.parent()
		row = index.row()
				
		dropIndicator = self.visualRect( index )
		dropIndicator.setLeft( self.viewport().rect().left() )
		dropIndicator.setRight( self.viewport().rect().right() )
		
		if Qt.ItemFlag.ItemIsDropEnabled in self.model().flags( index ):
			threshold = 0.25
		else:
			threshold = 0.5
		
		itemBounds = self.visualRect( index )
		topThreshold = itemBounds.y() + itemBounds.height() * threshold
		bottomThreshold = itemBounds.y() + itemBounds.height() * ( 1.0 - threshold )
		
		if position.y() < topThreshold:
			dropIndicator.setTop( itemBounds.top() )
			dropIndicator.setBottom( itemBounds.top() - 1 )
		elif position.y() >= bottomThreshold:
			dropIndicator.setTop( itemBounds.bottom() + 1 )
			dropIndicator.setBottom( itemBounds.bottom() )
			row += 1
		else:
			parent = index
			row = self.model().rowCount( parent )
		
		return row, parent, dropIndicator
	
	
	@override
	def dragMoveEvent( self, event: QtGui.QDragMoveEvent ) -> None:
		'''
		Draw drop indicator.
		'''
		
		_, _, dropIndicator = self.dropTargetForPosition( event.position().toPoint() )
		self.dropIndicatorRect = dropIndicator
		
		event.acceptProposedAction()
		self.viewport().update()
	
	
	@override
	def dropEvent( self, event: QtGui.QDropEvent ) -> None:
		if event.proposedAction() not in self.model().supportedDropActions():
			return
		
		dropRow, dropParent, _ = self.dropTargetForPosition( event.position().toPoint() )
		
		# Internal move.
		if event.proposedAction() is Qt.DropAction.MoveAction and event.source() is self:
			selectedIndexes = [
				QPersistentModelIndex( index )
				for index in self.selectedRowIndexes()
				if Qt.ItemFlag.ItemIsDragEnabled in self.model().flags( index )
			]
			
			if all(
				self.model().moveRow( index.parent(), index.row(), dropParent, dropRow )
				for index in selectedIndexes
			):
				event.acceptProposedAction()
		
		# All drop actions supported by the model.
		else:
			if self.model().dropMimeData(
				event.mimeData(),
				event.proposedAction(),
				dropRow,
				0,
				dropParent,
			):
				event.acceptProposedAction()
		
		# TODO: Is this necessary?
		self.stopAutoScroll()
		self.setState( QAbstractItemView.State.NoState )
		self.viewport().update()
	
	
	@override
	def paintEvent( self, event: QtGui.QPaintEvent ) -> None:
		'''
		Draw view content and drop indicator.
		TODO: Fix animations.
		'''
		
		painter = QPainter( self.viewport() )
		
		self.drawTree( painter, event.region() )
		
		# Draw drop indicator.
		if self.state() is QAbstractItemView.State.DraggingState and self.showDropIndicator():
			styleOption = QStyleOption()
			styleOption.initFrom( self )
			styleOption.rect = self.dropIndicatorRect	# pyright: ignore [reportAttributeAccessIssue]
			self.style().drawPrimitive(
				QStyle.PrimitiveElement.PE_IndicatorItemViewItemDrop,
				styleOption,
				painter,
				self,
			)
	
	
	@Slot()
	def newItem( self ) -> None:
		'''
		Insert new item.
		'''
		
		if selectedIndexes := self.selectedIndexes():
			# After last selected item.
			lastSelectedIndex = max( selectedIndexes, key = lambda index: index.row() )
			self.model().insertRow( lastSelectedIndex.row() + 1, lastSelectedIndex.parent() )
		else:
			# After last item.
			self.model().insertRow( self.model().rowCount() + 1 )
	
	
	@Slot()
	def deleteSelectedItems( self ) -> None:
		'''
		Delete selected items from table.
		'''
		
		selectedIndexes = [
			QPersistentModelIndex( index )
			for index in self.selectedIndexes()
			if index.column() == 0
		]
		
		for index in selectedIndexes:
			# TODO: Check deleting parent before child.
			self.model().removeRow( index.row(), index.parent() )



class EnumDelegate( QStyledItemDelegate ):
	'''
	`QStyledItemDelegate` with support for displaying and editing `Enum`s.
	'''
	
	@override
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
	
	
	@override
	def setEditorData( self, editor: QWidget, index: ModelIndex ) -> None:
		'''
		Sets the contents of the given `editor` to the data for the item at the given `index`.
		'''
		
		match value := index.model().data( index, Qt.ItemDataRole.EditRole ), editor:
			case Enum(), QComboBox() as enumEditor:
				enumEditor.setCurrentText( value.name )
			
			case _:
				super().setEditorData( editor, index )
	
	
	@override
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