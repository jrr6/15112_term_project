# atomic_elements.py
# Joseph Rotella (jrotella, F0)
#
# Contains "atomic" UI elements that interact directly with the canvas.

from modular_graphics import UIElement

class Rectangle(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = props.get('width', 0)
        self.height = props.get('height', 0)

    def draw(self, canvas):
        fill = self.props.get('fill', None)
        borderColor = self.props.get('borderColor', 'black')
        borderWidth = self.props.get('borderWidth', 1)
        canvas.createRectangle(0, 0, self.width, self.height, fill=fill,
                               outline=borderColor, width=borderWidth)

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
