# Toolbar.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI code for toolbar element.
# Note: Icons were created by me using Affinity Designer.

from modular_graphics import UIElement
from modular_graphics.input_elements import Button


class Toolbar(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.kButtonSize = 40
        self.kButtonStep = self.kButtonSize + 10
        self.xStart = 30
        self.yPos = 3

    def initChildren(self):
        x = self.xStart
        y = self.yPos
        for button in ['new', 'open', 'save', 'download', 'pie', 'bar', 'line',
                       'scatter', 'transpose', 'help']:
            self.appendChild(Button(button, x, y, img=f'img/{button}.png',
                                    width=self.kButtonSize,
                                    height=self.kButtonSize,
                                    action=lambda _, b=button: self.props[b]()))
            x += self.kButtonStep

    def getHeight(self):
        return self.kButtonSize

    def getWidth(self):
        return self.props['width']
