# input_elements.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI elements for user interaction.
import string
import time

from formulas import Cell
from modular_graphics.atomic_elements import Rectangle, Text
from modular_graphics import UIElement


class TextField(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.active = False
        self.selected = False
        self.height = props.get('height', 25)
        self.width = props.get('width', 100)
        self.displayText = props.get('text', '')
        self.sourceText = props.get('text', '')
        self.paddingX = 10
        self.paddingY = 5
        # TODO: Actually compute visibleChars using width/font?
        self.visibleChars = props.get('visibleChars', 13)
        self.doubleClickStart = 0
        self.kDoubleClickDelay = 0.75  # ms

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
                              text=self.displayText[-self.visibleChars:],
                              anchor=textAnchor))

    def onClick(self, event):
        now = time.time()
        if (self.props.get('editable', True)
                and not self.active
                and now < self.doubleClickStart + self.kDoubleClickDelay):
            self.activate()
        else:
            self.select()
            self.doubleClickStart = now

    def select(self, silent=False):
        # only editable cells meaningfully convey "selection" feedback
        if self.props.get('editable', True):
            self.selected = True
            self.makeKeyListener()
            self.getChild('border').props['borderColor'] = 'blue'
            self.getChild('border').props['borderWidth'] = 2

        # however, uneditable cells can still make a selection call (so they
        # can serve as a sort of button)
        if 'onSelect' in self.props and not silent:
            self.props['onSelect'](self)

    def activate(self):
        self.removeChild('placeholder')
        self.getChild('border').props['fill'] = 'lightblue'
        self.makeKeyListener()
        self._clipTextForEditing(True)
        self.active = True
        if 'onActivate' in self.props:
            self.props['onActivate'](self)

    # deselects the cell
    def deselect(self):
        self.selected = False
        self.doubleClickStart = 0  # don't jump to activation if clicked again
        self.resignKeyListener()
        self.getChild('border').props['borderColor'] = 'black'
        self.getChild('border').props['borderWidth'] = 1

    # exits active (editing) mode WITHOUT saving (call finishEditing to save!)
    # NOTE: does NOT deselect (cells stay selected after editing finishes!)
    def deactivate(self):
        self.active = False
        self.getChild('border').props['fill'] = None
        self._clipTextForEditing(False)

    # saves the current cell text (via the parent's method), then deactivates
    def finishEditing(self):
        if 'onChange' in self.props:
            self.props['onChange'](self)
        self.deactivate()

    def onKeypress(self, event):
        # key listeners that apply if selected OR active
        if event.key == 'Enter':
            if self.active:
                self.finishEditing()
            elif self.selected and self.props.get('editable', True):
                self.activate()
        elif event.key == 'Escape':
            if self.active:
                # deactivate WITHOUT saving
                self.deactivate()
            else:
                self.deselect()
            return
        elif event.key == 'Delete':
            if (self.selected and not self.active
                    and self.props.get('editable', True)):
                # Clear the cell and call appropriate listeners
                self.displayText = ''
                self.finishEditing()
            elif self.active:
                if event.commandDown:
                    self.displayText = ''
                elif event.optionDown:
                    # remove last space-separated entity
                    # TODO: maybe use rfind?
                    self.displayText = ' '.join(self.displayText.split(' ')[:-1])
                else:
                    self.displayText = self.displayText[:-1]

        if not self.active:
            # we're just selected -- don't update contents
            return

        # key listeners for text entry (only if active)
        if event.key == 'Space':
            self.displayText += ' '
        elif event.key in (string.ascii_letters + string.punctuation
                           + string.digits):
            self.displayText += event.key
        self._clipTextForEditing(True)

    def setText(self, text):
        self.displayText = text
        self._clipTextForEditing(self.active)

    def _clipTextForEditing(self, editing):
        if len(self.displayText) > self.visibleChars:
            if editing:
                visibleText = '…' + self.displayText[-self.visibleChars:]
            else:
                visibleText = self.displayText[:self.visibleChars] + '…'
        else:
            visibleText = self.displayText
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
