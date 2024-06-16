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
	dropIndicatorRect: QRect | None = None
	
	@override
	def __init__( self, parent: QWidget | None = None ) -> None:
		super().__init__( parent )
		
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
	def indexAt( self, point: QPoint ) -> QModelIndex:
		if ( index := super().indexAt( point ) ).isValid():
			return index
		
		return self.rootIndex()
	
	
	@override
	def visualRect( self, index: ModelIndex ) -> QRect:
		if index == self.rootIndex():
			return self.viewport().rect().adjusted( 0, 0, -1, -1 )
		
		return super().visualRect( index )
	
	
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
	
	
	def dropIndicatorPositionForIndex(
		self,
		index: ModelIndex,
		point: QPoint,
		includeCenter: bool,
	) -> QAbstractItemView.DropIndicatorPosition:
		'''
		Return in which position `point` is in relative to the `index` row.
		'''
		
		threshold = 0.25 if includeCenter else 0.5
		rect = self.visualRect( index )
		topThreshold = rect.y() + rect.height() * threshold
		bottomThreshold = rect.y() + rect.height() * ( 1.0 - threshold )
		
		if point.y() < topThreshold:
			return QAbstractItemView.DropIndicatorPosition.AboveItem
		
		if point.y() >= bottomThreshold:
			return QAbstractItemView.DropIndicatorPosition.BelowItem
		
		return QAbstractItemView.DropIndicatorPosition.OnItem
	
	
	def dropIndicatorForIndex(
		self,
		index: ModelIndex,
		position: QAbstractItemView.DropIndicatorPosition
	) -> QRect:
		'''
		Return the drop indicator rect for a given `index` and `position` relative to this index.
		'''
		
		dropIndicator = self.visualRect( index )
		dropIndicator.setLeft( self.viewport().rect().left() )
		dropIndicator.setRight( self.viewport().rect().right() )
		
		if position is QAbstractItemView.DropIndicatorPosition.AboveItem:
			dropIndicator.setBottom( dropIndicator.top() - 1 )
		elif position is QAbstractItemView.DropIndicatorPosition.BelowItem:
			dropIndicator.setTop( dropIndicator.bottom() + 1 )
		
		return dropIndicator
	
	
	def dropTargetForEvent(
		self,
		event: QtGui.QDropEvent,
	) -> tuple[int | None, QModelIndex, QRect | None]:
		'''
		Calculate drop index and drop indicator based on vertical position.
		'''
		
		position = event.position().toPoint()
		indexAtCursor = self.indexAt( position )
		
		# Append to root index when dropped on viewport.
		if indexAtCursor == self.rootIndex():
			indexAtCursor = self.model().index(
				self.model().rowCount( indexAtCursor ) - 1,
				0,
				indexAtCursor,
			)
		
		# Drop as child of `indexAtCursor`.
		canDropOnItem = self.model().canDropMimeData(
			event.mimeData(),
			event.dropAction(),
			0,
			indexAtCursor.column(),
			indexAtCursor,
		)
		
		# Drop as sibling of `indexAtCursor`.
		canDropBesidesItem = self.model().canDropMimeData(
			event.mimeData(),
			event.dropAction(),
			indexAtCursor.row(),
			indexAtCursor.column(),
			indexAtCursor.parent(),
		)
		
		aboveItem = QAbstractItemView.DropIndicatorPosition.AboveItem
		onItem = QAbstractItemView.DropIndicatorPosition.OnItem
		belowItem = QAbstractItemView.DropIndicatorPosition.BelowItem
		
		cursorOnTop = self.dropIndicatorPositionForIndex( indexAtCursor, position, False ) is aboveItem
		cursorOnCenter = self.dropIndicatorPositionForIndex( indexAtCursor, position, True ) is onItem
		cursorOnBottom = self.dropIndicatorPositionForIndex( indexAtCursor, position, False ) is belowItem
		
		# If we can't drop besides then the whole cell goes to "on item".
		if canDropOnItem and ( cursorOnCenter or not canDropBesidesItem ):
			return (
				0,
				indexAtCursor,
				self.dropIndicatorForIndex( indexAtCursor, onItem ),
			)
		
		if canDropBesidesItem and cursorOnTop:
			return (
				indexAtCursor.row(),
				indexAtCursor.parent(),
				self.dropIndicatorForIndex( indexAtCursor, aboveItem ),
			)
		
		if canDropBesidesItem and cursorOnBottom:
			return (
				indexAtCursor.row() + 1,
				indexAtCursor.parent(),
				self.dropIndicatorForIndex( indexAtCursor, belowItem ),
			)
		
		return None, QModelIndex(), None
	
	
	@override
	def dragMoveEvent( self, event: QtGui.QDragMoveEvent ) -> None:
		'''
		Draw drop indicator.
		TODO:
		Get drag action from source index and not method.
		Get all drop actions in target view/model
		From overlap of source drag and target drop per index show rect.
		'''
		
		dropRow, _, self.dropIndicatorRect = self.dropTargetForEvent( event )
		
		if dropRow is not None:
			event.acceptProposedAction()
		else:
			event.ignore()
		
		self.viewport().update()
	
	
	@override
	def dropEvent( self, event: QtGui.QDropEvent ) -> None:
		dropRow, dropParent, self.dropIndicatorRect = self.dropTargetForEvent( event )
		
		assert dropRow is not None
		assert event.proposedAction() in self.model().supportedDropActions()
		
		if event.proposedAction() is Qt.DropAction.MoveAction and event.source() is self:
			# Internal move.
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
		else:
			# All drop actions supported by the model.
			if self.model().dropMimeData(
				event.mimeData(),
				event.proposedAction(),
				dropRow,
				0,
				dropParent,
			):
				event.acceptProposedAction()
		
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
		if (
			self.dropIndicatorRect
			and self.state() is QAbstractItemView.State.DraggingState
			and self.showDropIndicator()
		):
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