# SpreadsheetApp.py
# Joseph Rotella (jrotella, F0)
#
# Main code file -- contains top-level UI for spreadsheet app
import os

from data_visualization import ChartData, ChartType
from formulae import Cell
from modular_graphics import UIElement, App
from modular_graphics.atomic_elements import Rectangle
from ui_components import SpreadsheetGrid, Confirmation, FileSelector, Toolbar, \
    SheetSelector, HelpScreen
from utils import splitEscapedString


class SpreadsheetScene(UIElement):
    kChartDelimiter = '/'

    def __init__(self):
        # TODO: This could probably be even bigger
        super().__init__('scene', 0, 0, {})
        self.kGridX = 5
        self.width = 2 * self.kGridX + SpreadsheetGrid.siderWidth\
            + SpreadsheetGrid.numCols * SpreadsheetGrid.colWidth
        self.height = 750
        self.sheets = [Sheet.defaultEmpty()]
        self.activeSheet = 0

    def initChildren(self):
        self.makeKeyListener()
        # create toolbar now, add LAST so it's topmost
        toolbar = Toolbar('toolbar', 0, 0, width=self.width,
                          new=self.newDoc, open=self.open, save=self.save,
                          pie=self.chartHandler(ChartType.PIE),
                          line=self.chartHandler(ChartType.LINE),
                          scatter=self.chartHandler(ChartType.SCATTER),
                          bar=self.chartHandler(ChartType.BAR),
                          download=lambda: self.getChild('grid').startImport(),
                          transpose=lambda:
                          self.getChild('grid').transposeSelection(),
                          help=lambda: self.runModal(HelpScreen()))

        gridX = self.kGridX
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
        self.appendChild(SheetSelector('sheet-select', gridX,
                                       gridY + grid.getHeight(),
                                       sheets=self.sheets,
                                       active=self.activeSheet,
                                       onSelect=self.saveCurrentSheetAndOpen,
                                       onAdd=self.createSheet,
                                       onDelete=self.deleteSheet,
                                       onRename=self.renameSheet))

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

    def createSheet(self):
        newIdx = len(self.sheets)
        name = Sheet.kDefaultSheetPrefix + str(newIdx + 1)
        self.sheets.append(Sheet(name, {}, []))
        # we don't need to refresh sheet selector b/c sCSAO does it for us
        self.saveCurrentSheetAndOpen(newIdx)

    def saveCurrentSheetAndOpen(self, sheetIndex):
        # save the current sheet
        self.storeCurrentSheet()
        # open the new sheet, except avoid reload if we're re-opening the same
        if sheetIndex != self.activeSheet:
            # don't reopen the existing sheet
            # (since this would also mess up double-click to configure)
            self.openSheet(sheetIndex)

    def openSheet(self, sheetIndex):
        Cell.loadRawCells(self.sheets[sheetIndex].cells)
        self.getChild('grid').reload(self.sheets[sheetIndex].charts)
        self.activeSheet = sheetIndex
        self.getChild('sheet-select').props['active'] = sheetIndex
        # TODO: If we didn't wipe everything out every time, we could make 2x-
        #       clicking without first selecting trigger config
        self.getChild('sheet-select').refresh()

    # loads the modified sheet contents into the app-level sheets list
    def storeCurrentSheet(self):
        self.sheets[self.activeSheet].charts = self.getChild('grid').charts
        self.sheets[self.activeSheet].cells = Cell.getRawCells()

    def deleteSheet(self, index):
        if index > self.activeSheet:
            nextSheet = self.activeSheet
        else:
            nextSheet = max(self.activeSheet - 1, 0)
        self.sheets.pop(index)
        if len(self.sheets) == 0:
            self.sheets.append(Sheet.defaultEmpty())
        self.openSheet(nextSheet)

    def renameSheet(self, index, name):
        self.sheets[index].name = name
        self.getChild('sheet-select').refresh()

    def newDoc(self):
        self.storeCurrentSheet()
        isUnmodified = len(self.sheets) == 1
        if isUnmodified:
            firstSheetUnmodified = (len(self.sheets[0].charts) == 0
                                    and len(self.sheets[0].cells) == 0)
            isUnmodified = isUnmodified and firstSheetUnmodified

        if not isUnmodified:
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
        # keep the ref to self.sheets so we don't have to re-assign props to
        # the sheet selector
        self.sheets.clear()
        self.sheets.append(Sheet.defaultEmpty())
        self.openSheet(0)

    def save(self):
        self.storeCurrentSheet()
        self.getChild('grid').deselectAllCellsButSender(None)  # hacky but works

        data = ''
        for sheet in self.sheets:
            chartObjs = sheet.charts
            charts = ''
            for chart in chartObjs:
                # Note that chart serializer escapes chart delimiter for us
                charts += chart.serialize() + SpreadsheetScene.kChartDelimiter
            charts = charts[:-1]
            cells = Cell.serializeRaw(sheet.cells)
            data += sheet.name + '\n' + cells + '\n' + charts + '\n'

        data = data[:-1]  # strip trailing newline to avoid confusion later on
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
                os.makedirs(parentDir, exist_ok=True)
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

                self.sheets.clear()

                curSheetName = ''
                curSheetCells = []
                curSheetCharts = []
                for i in range(len(lines)):
                    if i % 3 == 0:
                        # name line
                        curSheetName = lines[i]
                    elif i % 3 == 1:
                        # cells line
                        curSheetCells = Cell.deserializeRawCells(lines[i])
                    elif i % 3 == 2:
                        # charts line
                        chartStrs = splitEscapedString(lines[i],
                            SpreadsheetScene.kChartDelimiter)
                        curSheetCharts = []
                        for chartStr in chartStrs:
                            chartStr = chartStr.replace(
                                '\\' + SpreadsheetScene.kChartDelimiter,
                                SpreadsheetScene.kChartDelimiter)
                            chart = ChartData.deserialize(chartStr)
                            if chart is not None:
                                curSheetCharts.append(chart)
                        self.sheets.append(
                            Sheet(curSheetName, curSheetCells, curSheetCharts))

                if len(self.sheets) == 0:  # in case file empty
                    self.sheets.append(Sheet.defaultEmpty())

                # open the first sheet, which also reloads the grid
                self.openSheet(0)
        except:
            self.runModal(Confirmation(
                message=f'The file {path} could not be read.'))
            return


class Sheet:
    kDefaultSheetPrefix = 'Sheet'

    def __init__(self, name: str, cells: dict, charts: list):
        self.name = name
        self.cells = cells
        self.charts = charts

    @staticmethod
    def defaultEmpty():
        return Sheet(Sheet.kDefaultSheetPrefix + '1', {}, [])

if __name__ == '__main__':
    App.load('SimpleSheets', SpreadsheetScene())
