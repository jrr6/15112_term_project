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

                existingText = str(Cell.getValue(cellRow, cellCol))
                # TODO: Ensure that text field properly truncates when scrolling
                #       (may want to move truncation logic to TextField)
                self.appendChild(TextField(f'{rowNum},{colNum}', x, y,
                                           placeholder='', width=self.colWidth,
                                           height=self.rowHeight,
                                           text=existingText,
                                           onChange=self.saveCell,
                                           onActivate=self.setActiveCell,
                                           onSelect=self.setSelectedCells))

        previewY = (1 + self.numRows) * self.rowHeight
        self.appendChild(TextField('preview', 0, previewY,  placeholder='',
                                   width=self.getWidth(), height=self.rowHeight,
                                   editable=False))

        self.makeKeyListener()

    # called by text field after new value entered
    # NOTE: this might be called by a selected-but-not-active cell,
    #       so ALWAYS use sender instead of (possibly-None) self.activeCell
    def saveCell(self, sender):
        print(Cell._cells.keys())
        row, col = map(lambda x: int(x), sender.name.split(','))
        row += self.curTopRow
        col += self.curLeftCol
        if sender.displayText == '':
            Cell.delete(row, col)
        else:
            try:
                print(f'saving cell {sender.name}')
                Cell.setRaw(row, col, sender.displayText)
            except:
                sender.setText('SYNTAX-ERROR')
                return

            try:
                sender.setText(str(Cell.getValue(row, col)))
            except:
                sender.setText('RUNTIME-ERROR')

        # at least for now, onChange and "onDeactivate" are the same thing,
        # so this is our one-stop shop to note that the cell is no longer active
        self.activeCell = None

    def scroll(self, direction):
        # save current cell if we're in one
        if self.activeCell:
            self.activeCell.finishEditing()

        drow, dcol = direction.value
        self.curTopRow += drow
        self.curLeftCol += dcol
        self.removeAllChildren()
        # TODO: Is recreating everything every time going to become too costly?
        #       If so, could try to change (x, y) of existing cells.
        self.initChildren()

    def getWidth(self):
        return self.numCols * self.colWidth + self.siderWidth

    def getHeight(self):
        return (1 + self.numRows) * self.rowHeight

    def setActiveCell(self, sender):
        if self.activeCell:
            self.activeCell.finishEditing()
        self.activeCell = sender

    def setSelectedCells(self, sender):
        if self.activeCell:
            self.activeCell.deactivate()
            self.activeCell = None
        if sender.name[0] == 'H':  # whole column
            for cell in self.selectedCells:
                # TODO: we should also finishEditing, but first we need to figure
                #       out how the heck we're managing to save without it...
                cell.deactivate()
                cell.deselect()
            col = sender.name[1:]
            self.selectedCells =\
                [cell for cell in self.children
                 if SpreadsheetGrid.rowColFromCellName(cell.name)[1] == col]
            for cell in self.selectedCells:
                cell.select(silent=True)
        elif sender.name[0] == 'S':  # whole row
            for cell in self.selectedCells:
                # TODO: See above
                cell.deactivate()
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
                    # TODO: See above
                    cell.deactivate()
                    cell.deselect()
            self.selectedCells = [sender]

        if len(self.selectedCells) == 1:
            selectedRow, selectedCol = SpreadsheetGrid.rowColFromCellName(
                self.selectedCells[0].name)
            self.getChild('preview').setText(Cell.getValue(selectedRow,
                                                           selectedCol))

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
