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
from modular_graphics.atomic_elements import Rectangle, Image
from ui_components import SpreadsheetGrid, Confirmation, FileSelector, Toolbar


class SpreadsheetScene(UIElement):
    kChartDelimiter = '/'

    def __init__(self):
        # TODO: This could probably be even bigger
        self.width = 1020
        self.height = 720
        super().__init__('scene', 0, 0, {})

    def initChildren(self):
        self.makeKeyListener()
        # create toolbar now, add LAST so it's topmost
        toolbar = Toolbar('toolbar', 0, 0, width=self.width,
                          new=self.newDoc, open=self.open, save=self.save,
                          pie=self.chartHandler(ChartType.PIE),
                          line=self.chartHandler(ChartType.LINE),
                          scatter=self.chartHandler(ChartType.SCATTER),
                          bar=self.chartHandler(ChartType.BAR),
                          download=lambda: self.getChild('grid').startImport())

        gridX = 5
        gridY = toolbar.getHeight() + 10
        grid = SpreadsheetGrid('grid', gridX, gridY)
        self.appendChild(grid)

        # UI scaffolding to hide off-screen charts
        self.appendChild(Rectangle('left-hider', 0, 0,
                                   width=gridX, height=self.height,
                                   fill='white', borderColor=''))
        self.appendChild(Rectangle('right-hider', gridX + grid.getWidth() + 1,
                                   0, height=self.height,
                                   width=self.width - grid.getWidth(),
                                   fill='white', borderColor=''))
        self.appendChild(Rectangle('top-hider', 0, 0,
                                   width=self.width, height=gridY,
                                   fill='white', borderColor=''))
        self.appendChild(Rectangle('bot-hider', gridX,
                                   gridY + grid.getHeight() + 1,
                                   width=self.width,
                                   height=self.height - grid.getHeight(),
                                   fill='white', borderColor=''))

        # append the toolbar last so it sits atop scaffolding
        self.appendChild(toolbar)

        # CHART TESTING CODE
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
        elif event.key == 'o' and event.commandDown:
            self.open()
        elif event.key == 'n' and event.commandDown:
            self.newDoc()

    def newDoc(self):
        curChartsEmpty = len(self.getChild('grid').charts) == 0
        curCellsEmpty = Cell.empty()

        if not (curChartsEmpty and curCellsEmpty):
            self.runModal(Confirmation(
                message='Do you want to create a new document? '
                        'Unsaved changes will be lost.',
                onConfirm=self.resetDoc))
        else:
            self.resetDoc()

    def chartHandler(self, chartType):
        def handler():
            self.getChild('grid').insertChart(chartType)
        return handler

    def resetDoc(self):
        Cell.overwriteFromData(None)
        self.getChild('grid').reload([])

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

    def open(self):
        grid = self.getChild('grid')
        grid.deselectAllCellsButSender(None)  # hacky, but it works
        self.runModal(FileSelector(message='Open File',
                                   onSubmit=self.readFile))

    def writeFile(self, path, data):
        if os.path.exists(path):
            self.runModal(Confirmation(
                message=f'The file {path} already exists. '
                        f'Do you want to overwrite it?',
                onConfirm=lambda path=path, data=data:
                self.doWrite(path, data)))
        else:
            lastSep = path.rfind('/')
            if lastSep > -1:
                parentDir = path[:lastSep]
                os.makedirs(parentDir)
            self.doWrite(path, data)

    def doWrite(self, path, data):
        with open(path, 'w') as file:
            file.write(data)

    def readFile(self, path):
        if not os.path.isfile(path):
            self.runModal(Confirmation(
                message=f'There exists no file {path}.'))
            return

        try:
            with open(path, 'r') as file:
                # note -- we want to get empty strings, so splitlines() and
                # other "clever" Python built-ins are a bad idea
                lines = file.read().split('\n')

                # if it's an empty file, just clear everything
                if len(lines) == 0:
                    Cell.overwriteFromData(None)
                    charts = []
                else:
                    Cell.overwriteFromData(lines[0])
                    # if there are no charts, don't bother parsing
                    if len(lines) == 1:
                        charts = []
                    else:
                        chartStrs = lines[1].split(SpreadsheetScene.kChartDelimiter)
                        charts = []
                        for chartStr in chartStrs:
                            chart = ChartData.deserialize(chartStr)
                            if chart is not None:
                                charts.append(chart)

                # reload the grid with new data
                self.getChild('grid').reload(charts)
        except:
            self.runModal(Confirmation(
                message=f'The file {path} could not be read.'))
            return

if __name__ == '__main__':
    App.load('SimpleSheets', SpreadsheetScene())
