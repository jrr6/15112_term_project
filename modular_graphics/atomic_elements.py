# atomic_elements.py
# Joseph Rotella (jrotella, F0)
#
# Contains "atomic" UI elements that interact directly with the canvas.
from typing import Union

from PIL import ImageTk
from PIL import Image as PILImage

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
                          font=self.props.get('font', '"Andale Mono" 12'),
                          anchor=self.props.get('anchor', 'center'))

    # user never directly interacts with text, so don't bother computing bounds
    def getHeight(self):
        return 0

    def getWidth(self):
        return 0

class Image(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.cached: Union[ImageTk.PhotoImage, None] = None

    def draw(self, canvas):
        if self.cached is None:
            img = PILImage.open(self.props['src'])
            if 'width' in self.props:
                width = self.props['width']
            else:
                width = img.width
            if 'height' in self.props:
                height = self.props['height']
            else:
                height = img.height

            if width != img.width or height != img.height:
                img = img.resize((width, height), resample=PILImage.ANTIALIAS)

            # sadly, we can't cache in init because it makes Tkinter unhappy
            self.cached = ImageTk.PhotoImage(img)

        anchor = self.props.get('anchor', None)

        canvas.createImage(0, 0, image=self.cached, anchor=anchor)

    def getWidth(self):
        return self.cached.width() if self.cached else 0

    def getHeight(self):
        return self.cached.height() if self.cached else 0
