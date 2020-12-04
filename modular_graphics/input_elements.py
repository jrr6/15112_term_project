# input_elements.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI elements for user interaction.

import string
import time

from modular_graphics import UIElement
from modular_graphics.atomic_elements import Rectangle, Text

class DoubleClickable(object):
    def __init__(self, *args):
        super().__init__(*args)  # play nice with UIElement
        self.doubleClickStart = 0
        self.kDoubleClickDelay = 0.75  # ms

    def isDoubleClick(self):
        now = time.time()
        if now < self.doubleClickStart + self.kDoubleClickDelay:
            self.doubleClickStart = 0
            return True
        else:
            self.doubleClickStart = now
            return False

    def resetDoubleClick(self):
        self.doubleClickStart = 0

# TODO: Need to make UICell a subclass to avoid redundant code
class TextField(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        # Constants
        self.paddingX = 10

        # State
        self.active = False
        self.height = props.get('height', 25)
        self.width = props.get('width', 100)
        # TODO: Actually compute visibleChars using width/font?
        self.visibleChars = props.get('visibleChars', 13)
        self.text = props.get('text', '')

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
            textY = self.height // 2
            textAnchor = 'w'

        self.appendChild(Rectangle('border', 0, 0, width=self.width,
                                   height=self.height, fill=fill))
        self.appendChild(Text('placeholder', 10, self.height // 2,
                              text=placeholder,
                              fill='gray', anchor='w'))
        self.appendChild(Text('input', textX, textY,
                              text='', anchor=textAnchor))
        # populate input with correct clipping
        self._renderText(False)

    def onClick(self, event):
        if self.props.get('editable', True) and not self.active:
            self.activate()

    def activate(self):
        self.removeChild('placeholder')
        self.getChild('border').props['fill'] = 'lightblue'
        self.makeKeyListener()
        self._renderText(True)
        self.active = True
        if 'onActivate' in self.props:
            self.props['onActivate'](self)

    # exits active (editing) mode WITHOUT saving (call finishEditing to save!)
    # NOTE: does NOT deselect (cells stay selected after editing finishes!)
    def deactivate(self):
        self.active = False
        self.getChild('border').props['fill'] = None
        self._renderText(False)
        if 'onDeactivate' in self.props:
            self.props['onDeactivate'](self)

    # saves the current cell text (via the parent's method), then deactivates
    def finishEditing(self):
        if 'onChange' in self.props:
            self.props['onChange'](self)
        self.deactivate()

    def onKeypress(self, event):
        if event.key == 'Enter' or event.key == 'Escape':
            self.finishEditing()
        elif event.key == 'Delete':
            if event.commandDown:
                self.text = ''
            elif event.optionDown:
                # remove last space-separated entity
                # this is somewhat costly, but rfind was a huge headache
                self.text = ' '.join(self.text.split(' ')[:-1])
            else:
                self.text = self.text[:-1]

        # key listeners for text entry (only if active)
        if event.key == 'Space':
            self.text += ' '
        elif event.key in (string.ascii_letters + string.punctuation
                           + string.digits):
            self.text += event.key
        self._renderText(True)

    def _renderText(self, editing):
        if len(self.text) > self.visibleChars:
            if editing:
                visibleText = '…' + self.text[-self.visibleChars:]
            else:
                visibleText = self.text[:self.visibleChars] + '…'
        else:
            visibleText = self.text
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

    def onClick(self, event):
        if 'action' in self.props:
            self.props['action'](self)

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width
