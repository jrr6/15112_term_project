import string

from modular_graphics import UIElement, App

class SpreadsheetGrid(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.numRows = 10
        self.numCols = 4
        self.rowHeight = 25
        self.colWidth = 100
        self.siderWidth = 25

    def initChildren(self):
        for headerNum in range(self.numCols):
            x = headerNum * self.colWidth + self.siderWidth  # skip over siders
            label = chr(ord('A') + headerNum)
            self.appendChild(TextField(f'H{headerNum}', x, 0,
                                       placeholder='', editable=False,
                                       text=label, width=self.colWidth,
                                       height=self.rowHeight, fill='lightgray',
                                       align='center'))

        for siderNum in range(self.numRows):
            y = (1 + siderNum) * self.rowHeight  # don't label headers
            self.appendChild(TextField(f'H{headerNum}', 0, y,
                                       placeholder='', editable=False,
                                       text=str(siderNum + 1),
                                       width=self.siderWidth, fill='lightgray',
                                       height=self.rowHeight, align='center'))

        for rowNum in range(self.numRows):
            for colNum in range(self.numCols):
                x = colNum * self.colWidth + self.siderWidth  # skip siders
                y = (1 + rowNum) * self.rowHeight  # skip top row -- headers
                self.appendChild(TextField(f'{rowNum},{colNum}', x, y,
                                           placeholder='', width=self.colWidth,
                                           height=self.rowHeight))

    def getWidth(self):
        return self.numCols * self.colWidth

    def getHeight(self):
        return self.numRows * self.rowHeight

class TextField(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.active = False
        self.height = props.get('height', 25)
        self.width = props.get('width', 100)
        self.text = props.get('text', '')
        self.paddingX = 10
        self.paddingY = 5

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
        else:
            self.activate()

    def activate(self):
        self.removeChild('placeholder')
        self.getChild('border').props['fill'] = 'gray'
        self.makeKeyListener()
        self.active = True

    def deactivate(self):
        self.active = False
        self.getChild('border').props['fill'] = None
        self.resignKeyListener()

    def onKeypress(self, event):
        print(event.key)
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
        print('draw', self.name, self.x, self.y)
        canvas.createRectangle(0, 0, self.width, self.height, fill=fill)

    def getWidth(self):
        print(self.name, self.x, self.y)
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
        self.width = 600
        self.height = 600
        super().__init__('scene', 0, 10, {})

    def initChildren(self):
        self.appendChild(SpreadsheetGrid('grid', 100, 100))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


if __name__ == '__main__':
    App.load(Scene())
