# SpreadsheetGrid.py
# Joseph Rotella (jrotella, F0)
#
# Contains the SpreadsheetGrid UI component and logic.

import string
from enum import Enum

from formulae import Cell
from modular_graphics import UIElement
from ui_components.UICell import UICell
from ui_components.WebImporter import WebImporter


class Direction(Enum):
    RIGHT = (0, 1)
    LEFT = (0, -1)
    UP = (-1, 0)
    DOWN = (1, 0)

class SpreadsheetGrid(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.numRows = 20
        self.numCols = 7
        self.rowHeight = 25
        self.colWidth = 115
        self.siderWidth = 25
        self.curTopRow = 0
        self.curLeftCol = 0
        self.activeCell = None
        self.selectedCells = []

    def initChildren(self):
        for headerNum in range(self.numCols):
            x = headerNum * self.colWidth + self.siderWidth  # skip over siders
            label = chr(ord('A') + headerNum + self.curLeftCol)
            self.appendChild(UICell(f'H{headerNum}', x, 0,
                                    placeholder='', editable=False,
                                    text=label, width=self.colWidth,
                                    height=self.rowHeight, fill='lightgray',
                                    align='center',
                                    onSelect=self.setSelectedCells))

        for siderNum in range(self.numRows):
            y = (1 + siderNum) * self.rowHeight  # don't label headers
            label = siderNum + self.curTopRow + 1
            self.appendChild(UICell(f'S{siderNum}', 0, y,
                                    placeholder='', editable=False,
                                    text=str(label),
                                    width=self.siderWidth, fill='lightgray',
                                    height=self.rowHeight, align='center',
                                    onSelect=self.setSelectedCells))

        for rowNum in range(self.numRows):
            for colNum in range(self.numCols):
                x = colNum * self.colWidth + self.siderWidth  # skip siders
                y = (1 + rowNum) * self.rowHeight  # skip top row -- headers

                cellRow = rowNum + self.curTopRow
                cellCol = colNum + self.curLeftCol

                existingText = Cell.getRaw(cellRow, cellCol)
                existingOutput = (str(Cell.getValue(cellRow, cellCol))
                                  if Cell.hasFormula(cellRow, cellCol)
                                  else None)
                tf = UICell(f'{rowNum},{colNum}', x, y,
                            placeholder='', width=self.colWidth,
                            height=self.rowHeight,
                            text=existingText,
                            output=existingOutput,
                            onChange=self.saveCell,
                            onActivate=self.setActiveCell,
                            onSelect=self.setSelectedCells,
                            onDeactivate=self.handleDeactivation)
                self.appendChild(tf)

        previewY = (1 + self.numRows) * self.rowHeight
        self.appendChild(UICell('preview', 0, previewY, placeholder='',
                                width=self.getWidth(), height=self.rowHeight,
                                editable=False, visibleChars=115))

        self.makeKeyListener()

    # called by text field after new value entered
    # NOTE: this might be called by a selected-but-not-active cell,
    #       so ALWAYS use sender instead of (possibly-None) self.activeCell
    def saveCell(self, sender):
        row, col = self.absRowColFromCellName(sender.name)

        # NOTE: we need to call this here and NOT in deactivate because
        #       we need access to the OLD set of deps to unhighlight
        self.toggleDependencyHighlights(False)
        if sender.text == '':
            Cell.delete(row, col)
        else:
            try:
                print(f'saving cell {sender.name}')
                Cell.setRaw(row, col, sender.text)
            except:
                sender.setOutputText('SYNTAX-ERROR')
                return  # if we've already got a syntax error, don't try to eval

            # TODO: Escape doesn't work properly
            if Cell.hasFormula(row, col):
                try:
                    sender.setOutputText(str(Cell.getValue(row, col)))
                except:
                    sender.setOutputText('RUNTIME-ERROR')
                    return
            else:
                sender.setOutputText(None)

        # TODO: Something is up with dependents
        for cellRef in Cell.getDependents(row, col):
            depRow, depCol = cellRef.row, cellRef.col
            if (self.curLeftCol <= depCol < self.curLeftCol + self.numCols and
                    self.curTopRow <= depRow < self.curTopRow + self.numRows):
                self.renderCell(depRow, depCol)
        self.updatePreview()

    def renderCell(self, row, col):
        childRow, childCol = row - self.curTopRow, col - self.curLeftCol
        cell = self.getChild(f'{childRow},{childCol}')
        try:
            cell.setOutputText(str(Cell.getValue(row, col)))
        except:
            cell.setOutputText('RUNTIME-ERROR')
        cell.rerender()

    def scroll(self, direction):
        # save current cell if we're in one
        if self.activeCell:
            self.activeCell.finishEditing()

        drow, dcol = direction.value
        self.curTopRow += drow
        self.curLeftCol += dcol

        self.removeAllChildren()
        # Is recreating everything every time going to become too costly?
        # If so, could try to change (x, y) of existing cells.
        self.initChildren()

        # remap selected cells
        i = 0
        while i < len(self.selectedCells):
            selRow, selCol = SpreadsheetGrid.rowColFromCellName(
                self.selectedCells[i].name)
            selRow, selCol = int(selRow), int(selCol)
            selRow -= drow
            selCol -= dcol
            if 0 <= selRow < self.numRows and 0 <= selCol < self.numCols:
                self.selectedCells[i] = self.getChild(f'{selRow},{selCol}')
                self.selectedCells[i].select(silent=True)
                i += 1
            else:
                self.selectedCells.pop(i)

    def getWidth(self):
        return self.numCols * self.colWidth + self.siderWidth

    def getHeight(self):
        return (1 + self.numRows) * self.rowHeight

    def setActiveCell(self, sender):
        if self.activeCell:
            self.activeCell.finishEditing()
        self.activeCell = sender
        self.toggleDependencyHighlights(True)

    def handleDeactivation(self, sender):
        # Cells may redundantly "deactivate" for safety, so only update
        # self.activeCell if the current active cell is the one deactivating
        if sender is self.activeCell:
            self.activeCell = None

    def toggleDependencyHighlights(self, highlight):
        # we might have had a selected-but-not-active cell trigger this
        if not self.activeCell:
            return
        row, col = self.absRowColFromCellName(self.activeCell.name)
        for depRef in Cell.getShallowDependencies(row, col):
            print('setting dep', depRef)
            depRow, depCol = (depRef.row + self.curTopRow,
                              depRef.col + self.curLeftCol)
            self.getChild(f'{depRow},{depCol}').highlight('orange' if highlight
                                                          else None)

    def setSelectedCells(self, sender, modifier):
        if self.activeCell:
            self.activeCell.finishEditing()

        if (modifier is not None) and (len(self.selectedCells) > 0):
            if modifier == 'Command':
                # Command either adds another, or deselects current
                if sender in self.selectedCells:
                    self.selectedCells.remove(sender)
                    sender.deselect()
                else:
                    self.selectedCells.append(sender)
            elif modifier == 'Shift':
                self.blockSelect(sender)
        else:
            # Deselect everything but sender (if the sender's a header/sider,
            # it won't be in there anyway, so it's fine)
            for cell in self.selectedCells:
                if cell is not sender:  # clicking cell twice doesn't deselect
                    cell.deselect()

            if sender.name[0] == 'H' or sender.name == 'S':  # whole row/column
                # Select the entire col (index 1 in the tuple) if it's a header,
                # or row (index 0 in the tuple) if it's a sider
                rowColTupleIdx = 1 if sender.name[0] == 'H' else 0
                rowCol = int(sender.name[1:])  # the row/col we selected
                self.selectedCells = []
                for cell in self.children:
                    if SpreadsheetGrid.rowColFromCellName(
                            cell.name)[rowColTupleIdx] == rowCol:
                        self.selectedCells.append(cell)
                        cell.select(silent=True)
            else:  # individual cell
                self.selectedCells = [sender]
        self.updatePreview()

    # Selects a "block" of cells (i.e., shift-select)
    def blockSelect(self, sender):
        pivotCell = self.selectedCells[0]
        for i in range(1, len(self.selectedCells)):
            cell = self.selectedCells[i]
            if cell is not sender:
                cell.deselect()
        self.selectedCells = [pivotCell]
        pivRow, pivCol = SpreadsheetGrid.rowColFromCellName(
            pivotCell.name)
        selRow, selCol = SpreadsheetGrid.rowColFromCellName(sender.name)
        minRow, minCol = min(pivRow, selRow), min(pivCol, selCol)
        maxRow, maxCol = max(pivRow, selRow), max(pivCol, selCol)
        for row in range(minRow, maxRow + 1):
            for col in range(minCol, maxCol + 1):
                # The pivot is already in there, so don't re-add it
                # (Note that sender *isn't* in there yet, so it's fine.)
                if not (row == pivRow and col == pivCol):
                    cell = self.getChild(f'{row},{col}')
                    cell.select(silent=True)
                    self.selectedCells.append(cell)

    def updatePreview(self):
        if len(self.selectedCells) == 1:
            selectedRow, selectedCol = self.absRowColFromCellName(
                self.selectedCells[0].name)
            self.getChild('preview').setText(Cell.getRaw(selectedRow,
                                                         selectedCol))
        else:
            # TODO: Show some useful stats or something...
            self.getChild('preview').setText('Multiple cells selected')
            pass

    def onKeypress(self, event):
        if event.optionDown:
            if event.key == 'Right' and self.curLeftCol < 26 - self.numCols:
                self.scroll(Direction.RIGHT)
            elif event.key == 'Left' and self.curLeftCol > 0:
                self.scroll(Direction.LEFT)
            elif event.key == 'Up' and self.curTopRow > 0:
                self.scroll(Direction.UP)
            elif event.key == 'Down':
                self.scroll(Direction.DOWN)
        else:
            if self.selectedCells == []:
                return
            lastSelection = self.selectedCells[-1]
            lastRow, lastCol = SpreadsheetGrid.rowColFromCellName(
                lastSelection.name)
            # TODO: Implement cell navigation via keyboard input

        if event.key == 'i' and event.commandDown:
            if len(self.selectedCells) == 0:
                return

            importer = WebImporter(onImport=self.importWebTable)
            self.runModal(importer)

    def importWebTable(self, table):
        pass
        # RETURN TRUE/FALSE

    # returns row and column for cell with given name.
    # if name doesn't represent a body cell (e.g., header/sider/preview),
    # returns -1, -1
    @staticmethod
    def rowColFromCellName(name):
        if name[0] not in string.digits:
            return ['-1', '-1']
        row, col = name.split(',')
        return int(row), int(col)

    # returns the absolute (NOT relative-to-view) row, col of a given UI cell
    def absRowColFromCellName(self, name):
        row, col = SpreadsheetGrid.rowColFromCellName(name)
        return row + self.curTopRow, col + self.curLeftCol
