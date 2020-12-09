# SheetSelector.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI code for sheet switcher.
from modular_graphics import UIElement
from modular_graphics.input_elements import Button
from ui_components.SheetConfiguration import SheetConfiguration


class SheetSelector(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.kSheetButtonWidth = 110
        self.kAddButtonWidth = 20
        self.kButtonHeight = 20
        self.kActiveColor = 'LightCyan3'
        self.kVisibleChars = 14
        self.maxSheets = 10
        if 'sheets' not in self.props or 'active' not in self.props:
            raise Exception('Missing sheets description for sheet selector')
        if 'onSelect' not in self.props or 'onAdd' not in self.props\
                or 'onDelete' not in self.props or 'onRename' not in self.props:
            raise Exception('Cannot create sheet selector without handlers')

    def initChildren(self):
        sheets = self.props['sheets']
        xPos = 0
        for i in range(len(sheets)):
            fill = self.kActiveColor if i == self.props['active'] else None
            text = sheets[i].name
            if len(text) > self.kVisibleChars:
                text = text[:self.kVisibleChars] + '…'
            self.appendChild(Button(str(i), xPos, 0, text=text,
                                    width=self.kSheetButtonWidth,
                                    height=self.kButtonHeight,
                                    fill=fill,
                                    action=lambda _, i=i:
                                        self.props['onSelect'](i),
                                    doubleClickAction=lambda _, i=i:
                                        self.showConfigurator(i)))
            xPos += self.kSheetButtonWidth
        if len(sheets) < self.maxSheets:
            self.appendChild(Button('add', xPos, 0, text='+',
                                    width=self.kAddButtonWidth,
                                    height=self.kButtonHeight,
                                    action=lambda _: self.props['onAdd']()))
        self.makeKeyListener()

    def refresh(self):
        self.removeAllChildren()
        self.initChildren()

    def showConfigurator(self, sheetIndex):
        self.runModal(
            SheetConfiguration(index=sheetIndex,
                               name=self.props['sheets'][sheetIndex].name,
                               onSave=self.props['onRename'],
                               onDelete=self.props['onDelete']))

    def onKeypress(self, event):
        if event.key == '=' and event.commandDown:
            self.props['onAdd']()

    def getWidth(self):
        return self.kSheetButtonWidth * len(self.props['sheets'])\
               + self.kAddButtonWidth

    def getHeight(self):
        return self.kButtonHeight
