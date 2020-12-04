# SpreadsheetGrid.py
# Joseph Rotella (jrotella, F0)
#
# Contains the SpreadsheetGrid UI component and logic.

import string
from enum import Enum

from data_visualization import ChartType, Series, LineChart, ChartData, \
    BarChart, PieChart, ScatterChart
from formulae import Cell, CellRef
from modular_graphics import UIElement
from modular_graphics.atomic_elements import Rectangle
from ui_components.UICell import UICell
from ui_components.WebImporter import WebImporter, Table


class Direction(Enum):
    RIGHT = (0, 1)
    LEFT = (0, -1)
    UP = (-1, 0)
    DOWN = (1, 0)

class SpreadsheetGrid(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.numRows = 20
        self.numCols = 7
        self.rowHeight = 25
        self.colWidth = 115
        self.siderWidth = 25
        self.curTopRow = 0
        self.curLeftCol = 0
        self.activeCell = None
        self.selectedCells = []
        self.highlighted = []
        self.charts = []

    def initChildren(self):
        # Order to ensure correct overlapping:
        # 1. Body cells
        # 2. Charts (need to cover body cells but be covered by headers/siders)
        # 3. Headers/siders & preview

        # body cells
        for rowNum in range(self.numRows):
            for colNum in range(self.numCols):
                x = colNum * self.colWidth + self.siderWidth  # skip siders
                y = (1 + rowNum) * self.rowHeight  # skip top row -- headers

                cellRow = rowNum + self.curTopRow
                cellCol = colNum + self.curLeftCol

                existingText = Cell.getRaw(cellRow, cellCol)
                existingOutput = (str(Cell.getValue(cellRow, cellCol))
                                  if Cell.hasFormula(cellRow, cellCol)
                                  else None)
                tf = UICell(f'{rowNum},{colNum}', x, y,
                            placeholder='', width=self.colWidth,
                            height=self.rowHeight,
                            text=existingText,
                            output=existingOutput,
                            onChange=self.saveCell,
                            onActivate=self.setActiveCell,
                            onSelect=self.setSelectedCells,
                            onDeactivate=self.handleDeactivation,
                            onDeselect=self.handleDeselection)
                self.appendChild(tf)

        # rerender charts
        for i in range(len(self.charts)):
            self.appendChartChild(self.charts[i], i)

        # cover the corner
        self.appendChild(Rectangle('hider', 0, 0, width=self.siderWidth,
                                   height=self.rowHeight, fill='white',
                                   borderColor=''))

        # headers/siders
        for headerNum in range(self.numCols):
            x = headerNum * self.colWidth + self.siderWidth  # skip over siders
            label = chr(ord('A') + headerNum + self.curLeftCol)
            self.appendChild(UICell(f'H{headerNum}', x, 0,
                                    placeholder='', editable=False,
                                    text=label, width=self.colWidth,
                                    height=self.rowHeight, fill='lightgray',
                                    align='center',
                                    onSelect=self.setSelectedCells))

        for siderNum in range(self.numRows):
            y = (1 + siderNum) * self.rowHeight  # don't label headers
            label = siderNum + self.curTopRow + 1
            self.appendChild(UICell(f'S{siderNum}', 0, y,
                                    placeholder='', editable=False,
                                    text=str(label),
                                    width=self.siderWidth, fill='lightgray',
                                    height=self.rowHeight, align='center',
                                    onSelect=self.setSelectedCells))

        # preview
        previewY = (1 + self.numRows) * self.rowHeight
        self.appendChild(UICell('preview', 0, previewY, placeholder='',
                                width=self.getWidth(), height=self.rowHeight,
                                editable=False, visibleChars=115))

        self.makeKeyListener()

    # called by text field after new value entered
    # NOTE: this might be called by a selected-but-not-active cell,
    #       so ALWAYS use sender instead of (possibly-None) self.activeCell
    def saveCell(self, sender):
        row, col = self.absRowColFromCellName(sender.name)

        if sender.text == '':
            Cell.delete(row, col)
        else:
            try:
                print(f'saving cell {sender.name}')
                Cell.setRaw(row, col, sender.text)
            except:
                sender.setOutputText('SYNTAX-ERROR')
                return  # if we've already got a syntax error, don't try to eval

            if Cell.hasFormula(row, col):
                # This is already being rendered by the cell on deactivation
                self.renderCell(row, col, explicitRerender=False)
            else:
                sender.setOutputText(None)

        for cellRef in Cell.getDependents(row, col):
            depRow, depCol = cellRef.row, cellRef.col
            if self.absPosIsVisible(depRow, depCol):
                self.renderCell(depRow, depCol)
        self.updatePreview()

    def renderCell(self, row, col, explicitRerender=True):
        childRow, childCol = row - self.curTopRow, col - self.curLeftCol
        cell = self.getChild(f'{childRow},{childCol}')
        try:
            cell.setOutputText(str(Cell.getValue(row, col)))
        except:
            cell.setOutputText('RUNTIME-ERROR')
        if explicitRerender:
            cell.rerender()

    def scroll(self, direction):
        # save current cell if we're in one
        if self.activeCell:
            self.activeCell.finishEditing()

        drow, dcol = direction.value
        self.curTopRow += drow
        self.curLeftCol += dcol

        self.removeAllChildren()
        # Is recreating everything every time going to become too costly?
        # If so, could try to change (x, y) of existing cells.
        self.initChildren()

        # remap selected cells
        i = 0
        while i < len(self.selectedCells):
            selRow, selCol = SpreadsheetGrid.rowColFromCellName(
                self.selectedCells[i].name)
            selRow, selCol = int(selRow), int(selCol)
            selRow -= drow
            selCol -= dcol
            if 0 <= selRow < self.numRows and 0 <= selCol < self.numCols:
                # deselect the "old version" of this cell
                self.selectedCells[i].deselect(silent=True)
                # select the "new version"
                self.selectedCells[i] = self.getChild(f'{selRow},{selCol}')
                self.selectedCells[i].select(silent=True)
                i += 1
            else:
                self.selectedCells[i].deselect()  # removes for us!

    def getWidth(self):
        return self.numCols * self.colWidth + self.siderWidth

    def getHeight(self):
        return (1 + self.numRows) * self.rowHeight

    def setActiveCell(self, sender):
        if self.activeCell:
            self.activeCell.finishEditing()

        self.deselectAllCellsButSender(sender)
        self.activeCell = sender
        self.toggleDependencyHighlights(True)

    def handleDeactivation(self, sender):
        # Cells may redundantly "deactivate" for safety, so only update
        # self.activeCell if the current active cell is the one deactivating
        if sender is self.activeCell:
            # this is especially important if we're scrolling so we don't have
            # zombies!
            self.toggleDependencyHighlights(False)
            self.activeCell = None

    def handleDeselection(self, sender):
        if sender in self.selectedCells:
            self.selectedCells.remove(sender)

    def toggleDependencyHighlights(self, highlight):
        # we might have had a selected-but-not-active cell trigger this
        if not self.activeCell:
            return
        if len(self.highlighted) > 0:
            for cell in self.highlighted:
                cell.highlight(None)
            self.highlighted = []

        if not highlight:
            return

        row, col = self.absRowColFromCellName(self.activeCell.name)
        for depRef in Cell.getShallowDependencies(row, col):
            if self.absPosIsVisible(depRef.row, depRef.col):
                print('highlighting dep', depRef)
                depRow, depCol = (depRef.row - self.curTopRow,
                                  depRef.col - self.curLeftCol)
                child = self.getChild(f'{depRow},{depCol}')
                child.highlight('orange')
                self.highlighted.append(child)

    def setSelectedCells(self, sender, modifier):
        if self.activeCell and self.activeCell is not sender:
            self.activeCell.finishEditing()

        if (modifier is not None) and (len(self.selectedCells) > 0):
            if modifier == 'Command':
                # Command either adds another, or deselects current
                if sender in self.selectedCells:
                    sender.deselect()  # removes for us!
                else:
                    self.selectedCells.append(sender)
            elif modifier == 'Shift':
                self.blockSelect(sender)
        else:
            # Deselect everything but sender (if the sender's a header/sider,
            # it won't be in there anyway, so it's fine)
            self.deselectAllCellsButSender(sender)

            if sender.name[0] == 'H' or sender.name == 'S':  # whole row/column
                # Select the entire col (index 1 in the tuple) if it's a header,
                # or row (index 0 in the tuple) if it's a sider
                rowColTupleIdx = 1 if sender.name[0] == 'H' else 0
                rowCol = int(sender.name[1:])  # the row/col we selected
                self.selectedCells = []
                for cell in self.children:
                    if SpreadsheetGrid.rowColFromCellName(
                            cell.name)[rowColTupleIdx] == rowCol:
                        self.selectedCells.append(cell)
                        cell.select(silent=True)
            else:  # individual cell
                self.selectedCells = [sender]
        self.updatePreview()

    # Selects a "block" of cells (i.e., shift-select)
    def blockSelect(self, sender):
        pivotCell = self.selectedCells[0]
        self.deselectAllCellsButSender(sender, startIndex=1)
        self.selectedCells = [pivotCell]
        pivRow, pivCol = SpreadsheetGrid.rowColFromCellName(
            pivotCell.name)
        selRow, selCol = SpreadsheetGrid.rowColFromCellName(sender.name)
        minRow, minCol = min(pivRow, selRow), min(pivCol, selCol)
        maxRow, maxCol = max(pivRow, selRow), max(pivCol, selCol)
        for row in range(minRow, maxRow + 1):
            for col in range(minCol, maxCol + 1):
                # The pivot is already in there, so don't re-add it
                # (Note that sender *isn't* in there yet, so it's fine.)
                if not (row == pivRow and col == pivCol):
                    cell = self.getChild(f'{row},{col}')
                    cell.select(silent=True)
                    self.selectedCells.append(cell)

    # Utility method to deselect all cells except one (starting at some index)
    def deselectAllCellsButSender(self, sender, startIndex=0):
        i = startIndex
        while i < len(self.selectedCells):
            selCell = self.selectedCells[i]
            if selCell is not sender:
                self.selectedCells[i].deselect()  # removes for us!
            else:
                i += 1

    def updatePreview(self):
        if len(self.selectedCells) == 1:
            selectedRow, selectedCol = self.absRowColFromCellName(
                self.selectedCells[0].name)
            self.getChild('preview').setText(Cell.getRaw(selectedRow,
                                                         selectedCol))
        else:
            # TODO: Show some useful stats or something...
            self.getChild('preview').setText('Multiple cells selected')
            pass

    def onKeypress(self, event):
        if event.optionDown:
            if event.key == 'Right' and self.curLeftCol < 26 - self.numCols:
                self.scroll(Direction.RIGHT)
            elif event.key == 'Left' and self.curLeftCol > 0:
                self.scroll(Direction.LEFT)
            elif event.key == 'Up' and self.curTopRow > 0:
                self.scroll(Direction.UP)
            elif event.key == 'Down':
                self.scroll(Direction.DOWN)
        else:
            if self.selectedCells == []:
                return
            lastSelection = self.selectedCells[-1]
            lastRow, lastCol = SpreadsheetGrid.rowColFromCellName(
                lastSelection.name)
            # TODO: Implement cell navigation via keyboard input

        if event.key == 'i' and event.commandDown:
            if len(self.selectedCells) == 0:
                return

            target = self.selectedCells[0]
            # TODO: Is there a better way?
            # deselect everything to ensure we don't catch modal keystrokes
            self.deselectAllCellsButSender(None)
            importer = WebImporter(
                onImport=lambda table, target=target:
                self.importWebTable(table, target))
            self.runModal(importer)

        if event.key == 'l' and event.commandDown:
            self.insertChart(ChartType.LINE)
        elif event.key == 's' and event.commandDown:
            self.insertChart(ChartType.SCATTER)
        elif event.key == 'p' and event.commandDown:
            self.insertChart(ChartType.PIE)
        elif event.key == 'b' and event.commandDown:
            self.insertChart(ChartType.BAR)

    def importWebTable(self, table: Table, targetCell):
        numLetteredCols = 26
        selRow, selCol = self.absRowColFromCellName(targetCell.name)
        if selCol + table.longestRowLength >= numLetteredCols:
            return False

        curRow, curCol = selRow, selCol
        for row in table.rows:
            for cell in row:
                text = cell  # Tables want to be immutable
                if len(text) > 0 and text[0] == '=':
                    # No arbitrary code execution!
                    text = text[1:]
                Cell.setRaw(curRow, curCol, text)
                if self.absPosIsVisible(curRow, curCol):
                    relRow = curRow - self.curTopRow
                    relCol = curCol - self.curLeftCol
                    uiCell = self.getChild(f'{relRow},{relCol}')
                    uiCell.setOutputText(None)
                    uiCell.setText(text)
                curCol += 1
            curRow += 1
            curCol = selCol
        return True

    def insertChart(self, type: ChartType):
        # prepare refs for cells
        colRefs = {}
        for cell in self.selectedCells:
            row, col = self.absRowColFromCellName(cell.name)
            if col not in colRefs:
                colRefs[col] = []

            colRefs[col].append(CellRef(row, col))

        # ensure cols are in order
        for col in colRefs:
            colRefs[col].sort(key=lambda x: x.row)

        cols = sorted(colRefs.keys())

        # TODO: Dynamically determine whether to include titles
        # depTitles = False  # whether dependent series are labeled with titles
        # upperLeftValue = colRefs[cols[0]][0].getValue()  # avoid recomputing
        # if upperLeftValue.isdigit():
        #     indTitle = ''
        #     depTitles = False
        # else:
        #     indTitle = upperLeftValue
        #     colRefs[cols[0]].pop(0)  # don't use the title in the series
        #     depTitles = True
        #
        # if type == ChartType.PIE or type == ChartType.BAR:
        #     nextPossibleHeader = colRefs[cols[1]][0].getValue()
        #     # if the first dep col has no header, none of them does
        #     if nextPossibleHeader.isdigit():
        #         depTitles = True

        indSeries = None
        depSeries = []
        titles = []
        for i in range(len(cols)):
            title = colRefs[cols[i]][0]
            data = colRefs[cols[i]][1:]
            series = Series(title, data)
            titles.append(str(title.getValue()))
            if i == 0:
                indSeries = series
            else:
                depSeries.append(series)

        if len(titles) == 0:
            defaultTitle = 'New Chart'
        elif len(titles) == 1:
            defaultTitle = titles[0]
        elif len(titles) == 2:
            defaultTitle = ' and '.join(titles)
        else:
            defaultTitle = ', '.join(titles[:-1]) + f', and {titles[-1]}'

        if len(self.charts) > 0:
            ident = self.charts[-1].ident + 1
        else:
            ident = 0
        data = ChartData(ident, type, defaultTitle, indSeries, depSeries,
                         None, None, None, None,
                         self.curTopRow, self.curLeftCol, autocolor=True)
        self.addChart(data)

    # adds a chart to our app state and then appends it to the view
    def addChart(self, chartData):
        self.charts.append(chartData)
        self.appendChartChild(chartData)

    # appends a chart to the view based on chart data
    def appendChartChild(self, chartData):
        # TODO: Don't draw wildly off-screen charts
        x = ((chartData.col - self.curLeftCol) * self.colWidth)\
            + self.siderWidth
        y = ((chartData.row - self.curTopRow) + 1) * self.rowHeight

        chartTypeMap = {
            ChartType.PIE: PieChart,
            ChartType.LINE: LineChart,
            ChartType.SCATTER: ScatterChart,
            ChartType.BAR: BarChart
        }
        self.appendChild(chartTypeMap[chartData.chartType](
            f'chart{chartData.ident}',
            x, y, data=chartData,
            onDelete=lambda ident=chartData.ident: self.deleteChart(ident),
            onConfigure=lambda: self.deselectAllCellsButSender(None)
        ))

    def deleteChart(self, ident):
        self.removeChild(f'chart{ident}')
        i = 0
        while i < len(self.charts):
            if self.charts[i].ident == ident:
                self.charts.pop(i)
                return
            i += 1


    # returns row and column for cell with given name.
    # if name doesn't represent a body cell (e.g., header/sider/preview),
    # returns -1, -1
    @staticmethod
    def rowColFromCellName(name):
        if name[0] not in string.digits:
            return ['-1', '-1']
        row, col = name.split(',')
        return int(row), int(col)

    # returns the absolute (NOT relative-to-view) row, col of a given UI cell
    def absRowColFromCellName(self, name):
        row, col = SpreadsheetGrid.rowColFromCellName(name)
        return row + self.curTopRow, col + self.curLeftCol

    # returns whether the given absolute cell position is currently in view
    def absPosIsVisible(self, row, col):
        return (self.curLeftCol <= col < self.curLeftCol + self.numCols and
                self.curTopRow <= row < self.curTopRow + self.numRows)
