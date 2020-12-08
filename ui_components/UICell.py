# UICell.py
# Joseph Rotella (jrotella, f0)
#
# Contains the UI class for individual spreadsheet cells (not to be confused
# with the data model Cell class).

import string

from modular_graphics.atomic_elements import Rectangle, Text
from modular_graphics import UIElement
from modular_graphics.input_elements import DoubleClickable


# TODO: This should really be a subclass of TextField
class UICell(DoubleClickable, UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)

        # Constants
        self.paddingX = 10
        self.paddingY = 5

        # State
        self.active = False
        self.selected = False
        self.height = props['height']
        self.width = props['width']
        # TODO: Actually compute visibleChars using width/font?
        self.visibleChars = props.get('visibleChars', 14)
        self.text = props.get('text', '')
        self.formulaOutput = props.get('output', None)

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
        self.appendChild(Text('placeholder', 10, 5, text=placeholder,
                              fill='gray', anchor=textAnchor))
        self.appendChild(Text('input', textX, textY,
                              text='', anchor=textAnchor))
        # populate input with correct clipping
        self._renderText(False)

    def onClick(self, event):
        if (self.props.get('editable', True)
                and not self.active
                and self.isDoubleClick()):
            self.activate()
        else:
            if event.shiftDown:
                modifier = 'Shift'
            elif event.commandDown:
                modifier = 'Command'
            else:
                modifier = None
            self.select(modifier=modifier)

    def select(self, silent=False, modifier=None):
        # only editable cells meaningfully convey "selection" feedback
        if self.props.get('editable', True):
            self.selected = True
            self.makeKeyListener()
            self.getChild('border').props['borderColor'] = 'blue'
            self.getChild('border').props['borderWidth'] = 2

        # however, uneditable cells can still make a selection call (so they
        # can serve as a sort of button)
        if 'onSelect' in self.props and not silent:
            self.props['onSelect'](self, modifier)

    def activate(self):
        print('activate', self.name)
        self.removeChild('placeholder')
        self.getChild('border').props['fill'] = 'lightblue'
        self.makeKeyListener()
        self._renderText(True)
        self.active = True
        if 'onActivate' in self.props:
            self.props['onActivate'](self)

    # deselects the cell
    def deselect(self, silent=False):
        self.selected = False
        self.resetDoubleClick()  # don't jump to activation if clicked again
        self.resignKeyListener()
        self.getChild('border').props['borderColor'] = 'black'
        self.getChild('border').props['borderWidth'] = 1
        # TODO: Find some way to make sure preview updates when we deselect
        if 'onDeselect' in self.props and not silent:
            self.props['onDeselect'](self)

    # exits active (editing) mode WITHOUT saving (call finishEditing to save!)
    # NOTE: does NOT deselect (cells stay selected after editing finishes!)
    def deactivate(self):
        print('deactivate', self.name)
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
                self.text = ''
                self.formulaOutput = None
                self.finishEditing()
            elif self.active:
                if event.commandDown:
                    self.text = ''
                elif event.optionDown:
                    # remove last space-separated entity
                    # this is somewhat costly, but rfind was a huge headache
                    self.text = ' '.join(self.text.split(' ')[:-1])
                else:
                    self.text = self.text[:-1]

        if not self.active:
            # we're just selected -- don't update contents
            return

        # key listeners for text entry (only if active)
        if event.key == 'Space':
            self.text += ' '
        elif event.key in (string.ascii_letters + string.punctuation
                           + string.digits):
            self.text += event.key
        self._renderText(True)

    # Sets the text the text field holds
    def setText(self, text):
        self.text = str(text)
        self._renderText(self.active)
        # Our text has changed -- notify!
        if 'onChange' in self.props:
            self.props['onChange'](self)

    # Sets the output text for a text field containing a formula
    def setOutputText(self, formulaOutput):
        self.formulaOutput = formulaOutput

    # Manually trigger a rerender of the cell
    def rerender(self):
        self._renderText(self.active)

    # highlights the cell the given color, or resets highlight if None passed
    def highlight(self, color):
        self.getChild('border').props['fill'] = color

    def _renderText(self, editing):
        # NOTE: Do NOT use truthiness, since formulaOutput might be ''
        if not editing and self.formulaOutput is not None:
            text = self.formulaOutput
        else:
            text = self.text

        if len(text) > self.visibleChars:
            if editing:
                visibleText = '…' + text[-self.visibleChars:]
            else:
                visibleText = text[:self.visibleChars] + '…'
        else:
            visibleText = text
        self.getChild('input').props['text'] = visibleText

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width
