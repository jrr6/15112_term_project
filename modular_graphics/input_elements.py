# input_elements.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI elements for user interaction.
from modular_graphics import UIElement
from modular_graphics.atomic_elements import Rectangle, Text

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
