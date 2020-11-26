# SpreadsheetApp.py
# Joseph Rotella (jrotella, F0)
#
# Main code file -- contains UI & logic code for spreadsheet app

from enum import Enum

from formulas import Cell
from modular_graphics import UIElement, App
from modular_graphics.input_elements import TextField
from WebImportModal import Modal

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

                existingText = str(Cell.get(cellRow, cellCol).value())
                # TODO: Ensure that text field properly truncates when scrolling
                #       (may want to move truncation logic to TextField)
                self.appendChild(TextField(f'{rowNum},{colNum}', x, y,
                                           placeholder='', width=self.colWidth,
                                           height=self.rowHeight,
                                           text=existingText,
                                           onChange=self.saveCell,
                                           onActivate=self.setActiveCell,
                                           onSelect=self.setSelectedCells))

        # TODO: Add "preview" at the bottom
        # self.appendChild(TextField('preview', placeholder='',
        #                            width=self.getWidth(), height=self.rowHeight,
        #                            editable=False, text=existingText))

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
                Cell.get(row, col).setRaw(sender.text)
            except:
                sender.setText('SYNTAX-ERROR')
                return

            try:
                sender.setText(str(Cell.get(row, col).value()))
            except:
                sender.setText('RUNTIME-ERROR')

        # at least for now, onChange and "onDeactivate" are the same thing,
        # so this is our one-stop shop to note that the cell is no longer active
        self.activeCell = None

    def scroll(self, direction):
        # save current cell if we're in one
        if self.activeCell:
            self.activeCell.deactivate()

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
            self.activeCell.deactivate()
        self.activeCell = sender

    def setSelectedCells(self, sender):
        print(sender.name)
        if sender.name[0] == 'H':  # whole column
            for cell in self.selectedCells:
                cell.deactivate()
            col = sender.name[1:]
            self.selectedCells = [cell for cell in self.children
                                  if cell.name[cell.name.find(',') + 1:] == col]
            for cell in self.selectedCells:
                cell.select(True)
        elif sender.name[0] == 'S':  # whole row
            for cell in self.selectedCells:
                cell.deactivate()
            row = sender.name[1:]
            self.selectedCells = [cell for cell in self.children
                                  if cell.name[:cell.name.find(',')] == row]
            for cell in self.selectedCells:
                cell.select(True)
        else:  # individual cell
            for cell in self.selectedCells:
                if cell is not sender:  # clicking cell twice doesn't deselect
                    cell.deactivate()
            self.selectedCells = [sender]

    def onClick(self, event):
        if self.activeCell:
            self.activeCell.deactivate()

    def onKeypress(self, event):
        if event.key == 'Right' and self.curLeftCol < 26 - self.numCols:
            self.scroll(Direction.RIGHT)
        elif event.key == 'Left' and self.curLeftCol > 0:
            self.scroll(Direction.LEFT)
        elif event.key == 'Up' and self.curTopRow > 0:
            self.scroll(Direction.UP)
        elif event.key == 'Down':
            self.scroll(Direction.DOWN)
        # testing modals
        elif event.key == 'r':
            # modalWidth, modalHeight = 500, 300
            # modalX = self.getWidth() // 2 - modalWidth // 2
            # modalY = self.getHeight() // 2 - modalHeight // 2
            # self.appendChild(Modal('demo',
            #                        modalX, modalY,  width=modalWidth,
            #                        height=modalHeight,
            #                        message='Enter your favorite color:',
            #                        input=True))
            pass

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
