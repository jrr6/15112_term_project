# input_elements.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI elements for user interaction.
import string

from modular_graphics.atomic_elements import Rectangle, Text
from modular_graphics import UIElement


class TextField(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.active = False
        self.height = props.get('height', 25)
        self.width = props.get('width', 100)
        self.text = props.get('text', '')
        self.paddingX = 10
        self.paddingY = 5
        self.visibleChars = 12  # TODO: Actually compute this using width/font?

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
        self.appendChild(Text('input', textX, textY,
                              text=self.text[-self.visibleChars:],
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
        self.clipTextForEditing(True)
        self.active = True
        if 'onActivate' in self.props:
            self.props['onActivate'](self)

    def deactivate(self):
        self.active = False
        self.getChild('border').props['fill'] = None
        self.resignKeyListener()
        self.clipTextForEditing(False)
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
        self.clipTextForEditing(True)

    def clipTextForEditing(self, editing):
        if editing:
            visibleText = self.text[-self.visibleChars:]
        else:
            visibleText = self.text[:self.visibleChars]
        self.getChild('input').props['text'] = visibleText


    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class Button(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = props.get('width', 75)
        self.height = props.get('height', 25)

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
