# SpreadsheetApp.py
# Joseph Rotella (jrotella, F0)
#
# Main code file -- contains UI & logic code for spreadsheet app
import string
from enum import Enum

from formulas import Cell
from modular_graphics import UIElement, App
from modular_graphics.input_elements import TextField

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
            self.appendChild(TextField(f'H{headerNum}', x, 0,
                                       placeholder='', editable=False,
                                       text=label, width=self.colWidth,
                                       height=self.rowHeight, fill='lightgray',
                                       align='center',
                                       onSelect=self.setSelectedCells))

        for siderNum in range(self.numRows):
            y = (1 + siderNum) * self.rowHeight  # don't label headers
            label = siderNum + self.curTopRow + 1
            self.appendChild(TextField(f'S{siderNum}', 0, y,
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
                tf = TextField(f'{rowNum},{colNum}', x, y,
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
        self.appendChild(TextField('preview', 0, previewY,  placeholder='',
                                   width=self.getWidth(), height=self.rowHeight,
                                   editable=False, visibleChars=115))

        self.makeKeyListener()

    # called by text field after new value entered
    # NOTE: this might be called by a selected-but-not-active cell,
    #       so ALWAYS use sender instead of (possibly-None) self.activeCell
    def saveCell(self, sender):
        row, col = map(lambda x: int(x), sender.name.split(','))
        row += self.curTopRow
        col += self.curLeftCol
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

        for cellRef in Cell.getDependents(row, col):
            self.renderCell(cellRef.row, cellRef.col)
        self.updatePreview()

    def renderCell(self, row, col):
        childRow, childCol = row - self.curTopRow, col - self.curLeftCol
        cell = self.getChild(f'{childRow},{childCol}')
        try:
            cell.setOutputText(str(Cell.getValue(row, col)))
        except:
            cell.setOutputText('RUNTIME-ERROR')
        cell.rerender()

    # TODO: Preserve selected cell(s) on scroll
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

    def getWidth(self):
        return self.numCols * self.colWidth + self.siderWidth

    def getHeight(self):
        return (1 + self.numRows) * self.rowHeight

    def setActiveCell(self, sender):
        if self.activeCell:
            self.activeCell.finishEditing()
        self.activeCell = sender

    def handleDeactivation(self, sender):
        # Cells may redundantly "deactivate" for safety, so only update
        # self.activeCell if the current active cell is the one deactivating
        if sender is self.activeCell:
            self.activeCell = None

    def setSelectedCells(self, sender):
        if self.activeCell:
            self.activeCell.finishEditing()
        if sender.name[0] == 'H':  # whole column
            for cell in self.selectedCells:
                cell.deselect()
            col = sender.name[1:]
            self.selectedCells =\
                [cell for cell in self.children
                 if SpreadsheetGrid.rowColFromCellName(cell.name)[1] == col]
            for cell in self.selectedCells:
                cell.select(silent=True)
        elif sender.name[0] == 'S':  # whole row
            for cell in self.selectedCells:
                cell.deselect()
            row = sender.name[1:]
            self.selectedCells =\
                [cell for cell in self.children
                 if SpreadsheetGrid.rowColFromCellName(cell.name)[0] == row]
            for cell in self.selectedCells:
                cell.select(silent=True)
        else:  # individual cell
            for cell in self.selectedCells:
                if cell is not sender:  # clicking cell twice doesn't deselect
                    cell.deselect()
            self.selectedCells = [sender]
        self.updatePreview()

    def updatePreview(self):
        if len(self.selectedCells) == 1:
            selectedRow, selectedCol = list(map(lambda x: int(x),
                SpreadsheetGrid.rowColFromCellName(self.selectedCells[0].name)))
            selectedRow += self.curTopRow
            selectedCol += self.curLeftCol
            self.getChild('preview').setText(Cell.getRaw(selectedRow,
                                                         selectedCol))
        else:
            # TODO: Show some useful stats or something...
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

        # testing modals
        # if event.key == 'r':
            # modalWidth, modalHeight = 500, 300
            # modalX = self.getWidth() // 2 - modalWidth // 2
            # modalY = self.getHeight() // 2 - modalHeight // 2
            # self.appendChild(Modal('demo',
            #                        modalX, modalY,  width=modalWidth,
            #                        height=modalHeight,
            #                        message='Enter your favorite color:',
            #                        input=True))

    # returns row and column for cell with given name.
    # if name doesn't represent a body cell (e.g., header/sider/preview),
    # returns -1, -1
    @staticmethod
    def rowColFromCellName(name):
        if name[0] not in string.digits:
            return ['-1', '-1']
        return name.split(',')

class Scene(UIElement):
    def __init__(self):
        self.width = 850
        self.height = 575
        super().__init__('scene', 0, 0, {})

    def initChildren(self):
        self.appendChild(SpreadsheetGrid('grid', 5, 5))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


if __name__ == '__main__':
    App.load(Scene())
