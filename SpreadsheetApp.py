# SpreadsheetApp.py
# Joseph Rotella
#
# Main code file -- contains UI & logic code for spreadsheet app

import string
from enum import Enum

from modular_graphics import UIElement, App

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
        self.colWidth = 100
        self.siderWidth = 25
        self.cells = {}
        self.curTopRow = 0
        self.curLeftCol = 0
        self.activeCell = None

    def initChildren(self):
        for headerNum in range(self.numCols):
            x = headerNum * self.colWidth + self.siderWidth  # skip over siders
            label = chr(ord('A') + headerNum + self.curLeftCol)
            self.appendChild(TextField(f'H{headerNum}', x, 0,
                                       placeholder='', editable=False,
                                       text=label, width=self.colWidth,
                                       height=self.rowHeight, fill='lightgray',
                                       align='center'))

        for siderNum in range(self.numRows):
            y = (1 + siderNum) * self.rowHeight  # don't label headers
            label = siderNum + self.curTopRow + 1
            self.appendChild(TextField(f'H{headerNum}', 0, y,
                                       placeholder='', editable=False,
                                       text=str(label),
                                       width=self.siderWidth, fill='lightgray',
                                       height=self.rowHeight, align='center'))

        for rowNum in range(self.numRows):
            for colNum in range(self.numCols):
                x = colNum * self.colWidth + self.siderWidth  # skip siders
                y = (1 + rowNum) * self.rowHeight  # skip top row -- headers

                cellRow = rowNum + self.curTopRow
                cellCol = colNum + self.curLeftCol

                existingText = self.cells.get(f'{cellRow},{cellCol}', '')
                # TODO: Ensure that text field properly truncates when scrolling
                #       (may want to move truncation logic to TextField)
                self.appendChild(TextField(f'{rowNum},{colNum}', x, y,
                                           placeholder='', width=self.colWidth,
                                           height=self.rowHeight,
                                           text=existingText,
                                           onChange=self.saveCell,
                                           onActivate=self.setActiveCell))

        # TODO: Add "preview" at the bottom
        # self.appendChild(TextField('preview', placeholder='',
        #                            width=self.getWidth(), height=self.rowHeight,
        #                            editable=False, text=existingText))

        self.makeKeyListener()

    # called by text field after new value entered
    def saveCell(self, sender):
        row, col = map(lambda x: int(x), sender.name.split(','))
        row += self.curTopRow
        col += self.curLeftCol
        cellLabel = f'{row},{col}'
        if sender.text == '' and cellLabel in self.cells:
            del self.cells[cellLabel]
        else:
            self.cells[cellLabel] = sender.text

        # at least for now, onChange and "onDeactivate" are the same thing
        self.activeCell = None

    def scroll(self, direction):
        # save current cell if we're in one
        if self.activeCell:
            self.activeCell.deactivate()

        drow, dcol = direction.value
        self.curTopRow += drow
        self.curLeftCol += dcol
        self.removeAllChildren()
        self.initChildren()

    def getWidth(self):
        return self.numCols * self.colWidth + self.siderWidth

    def getHeight(self):
        return (1 + self.numRows) * self.rowHeight

    def setActiveCell(self, sender):
        if self.activeCell:
            self.activeCell.deactivate()
        self.activeCell = sender

    def onClick(self, x, y):
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

class TextField(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.active = False
        self.height = props.get('height', 25)
        self.width = props.get('width', 100)
        self.text = props.get('text', '')
        self.paddingX = 10
        self.paddingY = 5

    # TODO: Is recreating everything every time going to become too costly?
    #       If so, could try to change (x, y) of existing cells.
    def initChildren(self):
        placeholder = self.props.get('placeholder', 'Enter text')
        fill = self.props.get('fill', None)
        textAlign = self.props.get('align', None)
        if textAlign == 'center':
            textX = self.width // 2
            textY = self.height // 2
            textAnchor = 'center'
        else:  # align left
            textX = self.paddingX
            textY = self.paddingY
            textAnchor = 'nw'

        self.appendChild(Rectangle('border', 0, 0, width=self.width,
                                   height=self.height, fill=fill))
        self.appendChild(Text('placeholder', 10, 5, text=placeholder,
                              fill='gray', anchor='nw'))
        self.appendChild(Text('input', textX, textY, text=self.text,
                              anchor=textAnchor))

    def onClick(self, x, y):
        if self.active:
            self.deactivate()
        elif self.props.get('editable', True):
            self.activate()

    def activate(self):
        self.removeChild('placeholder')
        self.getChild('border').props['fill'] = 'lightblue'
        self.makeKeyListener()
        self.active = True
        if 'onActivate' in self.props:
            self.props['onActivate'](self)

    def deactivate(self):
        self.active = False
        self.getChild('border').props['fill'] = None
        self.resignKeyListener()
        if 'onChange' in self.props:
            self.props['onChange'](self)

    def onKeypress(self, event):
        if event.key == 'Enter' or event.key == 'Escape':
            self.deactivate()
            return

        if event.key == 'Space':
            self.text += ' '
        elif event.key == 'Delete':
            self.text = self.text[:-1]
        elif event.key in (string.ascii_letters + string.punctuation
                           + string.digits):
            self.text += event.key

        charsToShow = 12
        self.getChild('input').props['text'] = self.text[-charsToShow:]

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class Button(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = props.get('width', 200)
        self.height = props.get('height', 100)

    def initChildren(self):
        self.appendChild(Rectangle('border', 0, 0,
                                   width=self.width, height=self.height))
        if 'text' in self.props:
            self.appendChild(Text('label', self.width // 2, self.height // 2,
                                  text=self.props['text']))

    def onClick(self, x, y):
        if 'action' in self.props:
            self.props['action'](self)

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class Rectangle(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = props.get('width', 0)
        self.height = props.get('height', 0)

    def draw(self, canvas):
        fill = self.props.get('fill', None)
        canvas.createRectangle(0, 0, self.width, self.height, fill=fill)

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


class Text(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)

    def draw(self, canvas):
        canvas.createText(0, 0, text=self.props.get('text', ''),
                          font=self.props.get('font', 'Courier 12'),
                          anchor=self.props.get('anchor', 'center'))

    # user never directly interacts with text, so don't bother computing bounds
    def getHeight(self):
        return 0

    def getWidth(self):
        return 0

class Scene(UIElement):
    def __init__(self):
        self.width = 750
        self.height = 550
        super().__init__('scene', 0, 0, {})

    def initChildren(self):
        self.appendChild(SpreadsheetGrid('grid', 5, 5))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


if __name__ == '__main__':
    App.load(Scene())
