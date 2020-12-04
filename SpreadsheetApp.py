# SpreadsheetApp.py
# Joseph Rotella (jrotella, F0)
#
# Main code file -- contains top-level UI for spreadsheet app
from data_visualization import BarChart, PieChart, ChartData, Series, ChartType, \
    ScatterChart
from data_visualization.LineChart import LineChart
from modular_graphics import UIElement, App
from modular_graphics.atomic_elements import Rectangle
from ui_components import SpreadsheetGrid

class Scene(UIElement):
    def __init__(self):
        self.width = 850
        self.height = 575
        super().__init__('scene', 0, 0, {})

    def initChildren(self):
        gridX = 5
        gridY = 5
        self.appendChild(SpreadsheetGrid('grid', gridX, gridY))
        self.appendChild(Rectangle('side-hider', 0, 0,
                                   width=gridX, height=self.height,
                                   fill='white', borderColor=''))
        self.appendChild(Rectangle('top-hider', 0, 0,
                                   width=self.width, height=gridY,
                                   fill='white', borderColor=''))
        # chart = ChartData(ChartType.BAR, 'My Cool Chart',
        #                   Series('Attribute', ['Corporateness', 'Mundanity',
        #                                      'Use of Jargon']),
        #                   [Series('Widget 1', [9, 6, 10], color='red'),
        #                    Series('Widget 2', [8, 6, 7], color='yellow'),
        #                    Series('Widget 3', [1, 7, 3], color='blue')],
        #                   None, None, None, 10)

        # chart = ChartData(ChartType.PIE, '100%',
        #                   Series('Trait', ['Popularity', 'Smoothness']),
        #                   [Series('Apple', [7, 50], color='green'),
        #                    Series('Pumpkin', [5, 50], color='orange'),
        #                    Series('Banana', [9, 50], color='yellow')],
        #                   None, None, None, 60)

        # chart = ChartData(ChartType.LINE, 'Points in Space!',
        #                   Series('Time', [0, 5, 20, 10]),
        #                   [
        #                       Series('Eagle', [1, 3, 7, 4], 'green'),
        #                       Series('Falcon', [10, 5, 1, 2], 'red')
        #                   ], 0, 20, 0, 10)
        # self.appendChild(LineChart('test', 5, 5, data=chart))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


if __name__ == '__main__':
    App.load(Scene())
