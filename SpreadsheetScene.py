# SpreadsheetApp.py
# Joseph Rotella (jrotella, F0)
#
# Main code file -- contains top-level UI for spreadsheet app
import os

from data_visualization import BarChart, PieChart, ChartData, Series, ChartType, \
    ScatterChart
from data_visualization.LineChart import LineChart
from formulae import Cell
from modular_graphics import UIElement, App
from modular_graphics.atomic_elements import Rectangle
from ui_components import SpreadsheetGrid, Confirmation, FileSelector


class SpreadsheetScene(UIElement):
    kChartDelimiter = '/'

    def __init__(self):
        self.width = 850
        self.height = 575
        super().__init__('scene', 0, 0, {})

    def initChildren(self):
        self.makeKeyListener()
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

    def onKeypress(self, event):
        if event.key == 's' and event.commandDown:
            self.save()

    def save(self):
        grid = self.getChild('grid')
        grid.deselectAllCellsButSender(None)  # hacky, but it works
        chartObjs = grid.charts
        charts = ''
        for chart in chartObjs:
            # Note that chart serializer escapes chart delimiter for us
            charts += chart.serialize() + SpreadsheetScene.kChartDelimiter
        charts = charts[:-1]
        cells = Cell.serializeAll()
        data = cells + '\n' + charts
        # TODO: Check if this is an already-opened doc that we can overwrite
        self.runModal(FileSelector(message='Save File',
                                   onSubmit=lambda path, data=data:
                                   self.writeFile(path, data)))

    def writeFile(self, path, data):
        print('call', repr(path), data)
        if os.path.exists(path):
            print('exists')
            # TODO: Figure out modal method call dependency loop (we can't run this until the other dismisses…)
            self.runModal(Confirmation(
                message=f'The file {path} already exists. '
                        f'Do you want to overwrite it?'))
            return  # change this
        else:
            lastSep = path.rfind('/', -1)
            if lastSep > -1:
                parentDir = path[:lastSep]
                os.makedirs(parentDir)

        with open(path, 'w') as file:
            file.write(data)


if __name__ == '__main__':
    App.load(SpreadsheetScene())