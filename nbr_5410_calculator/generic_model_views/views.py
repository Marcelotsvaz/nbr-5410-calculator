'''
Views for `GenericItemModel`.
'''

from enum import Enum
from typing import TYPE_CHECKING, Any, cast, override

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

from nbr_5410_calculator.generic_model_views.models import (
	FieldOrder,
	GenericItem,
	GenericItemModel,
	ModelIndex,
)



# TODO: Figure out proper generic multiple inheritance with Qt.
if TYPE_CHECKING:
	class QAbstractItemViewT( QAbstractItemView ):	# pylint: disable = missing-class-docstring
		pass
else:
	class QAbstractItemViewT:	# pylint: disable = missing-class-docstring
		pass



class GenericViewMixin[ModelT: GenericItemModel[Any], ItemT: GenericItem]( QAbstractItemViewT ):
	'''
	Common `QAbstractItemView` overrides for `GenericItemModel`.
	'''
	
	fieldOrder: FieldOrder[ItemT] | None = None
	
	
	@override
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		
		self.dropIndicatorRect = QRect()
		
		self.setDragDropMode( QAbstractItemView.DragDropMode.DragDrop )
		self.setDefaultDropAction( Qt.DropAction.MoveAction )
	
	
	@override
	def model( self ) -> ModelT:
		return cast( ModelT, super().model() )
	
	
	@override
	def setModel( self, model: ModelT | None ) -> None:	# pyright: ignore [reportIncompatibleMethodOverride]
		super().setModel( model )
		
		if not model:
			return
		
		if isinstance( model, GenericItemModel ):	# TODO: QSortFilterProxyModel
			model.updateFieldOrder( self.fieldOrder )
		
		self.setRootIndex( model.index( 0, 0 ) )
	
	
	def selectedRowIndexes( self ) -> list[QModelIndex]:
		'''
		Return a sorted list of indexes, one for each selected row.
		'''
		
		return [
			index
			for index in sorted( self.selectedIndexes(), key = lambda index: index.row() )
			if index.column() == 0
		]
	
	
	def appendItem( self, item: ItemT ) -> None:
		'''
		Append `item` after last selected item.
		'''
		
		if selectedRowIndexes := self.selectedRowIndexes():
			# After last selected item.
			row = selectedRowIndexes[-1].row() + 1
			parent = selectedRowIndexes[-1].parent()
		else:
			# After last item.
			row = self.model().rowCount( self.rootIndex() )
			parent = self.rootIndex()
		
		self.model().insertItem( item, row, parent )
	
	
	@Slot()
	def deleteSelectedItems( self ) -> None:
		'''
		Delete selected items from table.
		'''
		
		selectedRowIndexes = [
			QPersistentModelIndex( index )
			for index in self.selectedRowIndexes()
		]
		
		for index in selectedRowIndexes:
			# TODO: Check deleting parent before child.
			self.model().removeRow( index.row(), index.parent() )
	
	
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
		
		# Get actions common to all items.
		actions = Qt.DropAction.ActionMask
		for index in selectedIndexes:
			actions &= self.model().dragActionsForIndex( index )
		
		if not actions:
			# TODO: Ignore this?
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
		# TODO: Should we care about supportedActions? Default should be based on what?
		# action = drag.exec( supportedActions, self.defaultDropAction() )
		action = drag.exec( actions )
		
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
			index = self.model().index(
				self.model().rowCount( self.rootIndex() ) - 1,
				0,
				self.rootIndex(),
			)
		
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
		TODO:
		Get drag action from source index and not method.
		Get all drop actions in target view/model
		From overlap of source drag and target drop per index show rect.
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
	def paintEvent( self, event: QtGui.QPaintEvent ) -> None:	# pyright: ignore [reportIncompatibleMethodOverride]
		'''
		Draw view content and drop indicator.
		TODO: Fix animations.
		'''
		
		# Temporally disable drop indicator so we can draw it ourselves later.
		oldShowDropIndicator = self.showDropIndicator()
		self.setDropIndicatorShown( False )
		super().paintEvent( event )
		self.setDropIndicatorShown( oldShowDropIndicator )
		
		# Draw drop indicator.
		painter = QPainter( self.viewport() )
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



class GenericListView[ModelT: GenericItemModel[Any], ItemT: GenericItem](	# pyright: ignore [reportIncompatibleMethodOverride]
	GenericViewMixin[ModelT, ItemT],
	QListView,
):
	'''
	List view for `GenericItemModel`.
	'''
	
	@override
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		
		self.setItemDelegate( GenericItemDelegate( self ) )
		
		self.setAlternatingRowColors( True )
		
		self.setSelectionMode( QAbstractItemView.SelectionMode.ExtendedSelection )
		# self.setSortingEnabled( True )



class GenericTreeView[ModelT: GenericItemModel[Any], ItemT: GenericItem](	# pyright: ignore [reportIncompatibleMethodOverride]
	GenericViewMixin[ModelT, ItemT],
	QTreeView,
):
	'''
	Tree view for `GenericItemModel`.
	'''
	
	@override
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		
		self.setItemDelegate( GenericItemDelegate( self ) )
		
		self.setUniformRowHeights( True )
		self.setAllColumnsShowFocus( True )
		self.setAlternatingRowColors( True )
		self.setAnimated( True )
		
		self.setSelectionMode( QAbstractItemView.SelectionMode.ExtendedSelection )
		# self.setSortingEnabled( True )
	
	
	def resizeColumnsToContents( self ) -> None:
		'''
		Resizes all columns given the size of their contents.
		'''
		
		for index in range( self.model().columnCount() ):
			self.resizeColumnToContents( index )
	
	
	@override
	def expandAll( self ) -> None:
		# This should avoid invalid calls to `QGenericItemModel.index`.
		if self.model().rowCount( self.rootIndex() ) > 0:
			super().expandAll()



class GenericItemDelegate( QStyledItemDelegate ):
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