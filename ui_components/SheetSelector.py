# SheetSelector.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI code for sheet switcher.
from modular_graphics import UIElement
from modular_graphics.input_elements import Button


class SheetSelector(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.kSheetButtonWidth = 100
        self.kAddButtonWidth = 20
        self.kButtonHeight = 20
        self.kActiveColor = 'LightCyan3'
        if 'sheets' not in self.props or 'active' not in self.props:
            raise Exception('Missing sheets description for sheet selector')
        if 'onSelect' not in self.props or 'onAdd' not in self.props:
            raise Exception('Cannot create sheet selector without handlers')

    def initChildren(self):
        sheets = self.props['sheets']
        xPos = 0
        for i in range(len(sheets)):
            fill = self.kActiveColor if i == self.props['active'] else None
            self.appendChild(Button(str(i), xPos, 0, text=sheets[i].name,
                                    width=self.kSheetButtonWidth,
                                    height=self.kButtonHeight,
                                    fill=fill,
                                    action=lambda _, i=i:
                                        self.props['onSelect'](i)))
            xPos += self.kSheetButtonWidth
        self.appendChild(Button('add', xPos, 0, text='+',
                                width=self.kAddButtonWidth,
                                height=self.kButtonHeight,
                                action=lambda _: self.props['onAdd']()))
        self.makeKeyListener()

    def refresh(self):
        self.removeAllChildren()
        self.initChildren()

    def onKeypress(self, event):
        if event.key == '=' and event.commandDown:
            self.props['onAdd']()

    def getWidth(self):
        return self.kSheetButtonWidth * len(self.props['sheets'])\
               + self.kAddButtonWidth

    def getHeight(self):
        return self.kButtonHeight
