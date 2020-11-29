# SpreadsheetApp.py
# Joseph Rotella (jrotella, F0)
#
# Main code file -- contains top-level UI for spreadsheet app

from modular_graphics import UIElement, App
from ui_components import SpreadsheetGrid

class Scene(UIElement):
    def __init__(self):
        self.width = 850
        self.height = 575
        super().__init__('scene', 0, 0, {})

    def initChildren(self):
        self.appendChild(SpreadsheetGrid('grid', 5, 5))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


if __name__ == '__main__':
    App.load(Scene())
