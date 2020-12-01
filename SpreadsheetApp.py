# SpreadsheetApp.py
# Joseph Rotella (jrotella, F0)
#
# Main code file -- contains top-level UI for spreadsheet app
from data_visualization import BarChart, ChartData, Series, ChartType
from modular_graphics import UIElement, App
from ui_components import SpreadsheetGrid

class Scene(UIElement):
    def __init__(self):
        self.width = 850
        self.height = 575
        super().__init__('scene', 0, 0, {})

    def initChildren(self):
        # self.appendChild(SpreadsheetGrid('grid', 5, 5))
        chart = ChartData(ChartType.BAR, 'My Cool Chart',
                          Series('Attribute', ['Corporateness', 'Mundanity',
                                             'Use of Jargon']),
                          [Series('Widget 1', [9, 6, 10], color='red'),
                           Series('Widget 2', [8, 6, 7], color='yellow'),
                           Series('Widget 3', [1, 7, 3], color='blue')],
                          None, None, None, 10)
        self.appendChild(BarChart('test', 5, 5, data=chart))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


if __name__ == '__main__':
    App.load(Scene())
