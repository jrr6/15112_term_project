# SpreadsheetGrid.py
# Joseph Rotella (jrotella, F0)
#
# Contains the SpreadsheetGrid UI component and logic.

import string
from enum import Enum

from data_visualization import ChartType, Series, LineChart, ChartData, \
    BarChart, PieChart, ScatterChart
from formulae import Cell, CellRef, Formula, Operator
from modular_graphics import UIElement
from modular_graphics.atomic_elements import Rectangle, Line
from ui_components.UICell import UICell
from ui_components.WebImporter import WebImporter, Table


class SpreadsheetGrid(UIElement):
    rowHeight = 30
    colWidth = 120
    numRows = 20
    numCols = 9
    siderWidth = 25

    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.curTopRow = 0
        self.curLeftCol = 0
        self.activeCell = None
        self.selectedCells = []
        self.highlighted = []
        self.charts = []
        self.dragStartX = 0
        self.dragStartY = 0
        self.dragThreshold = 2

    def draw(self, canvas):
        super().draw(canvas)

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
                if Cell.hasFormula(cellRow, cellCol):
                    existingOutput = str(Cell.getValue(cellRow, cellCol))
                elif str(Cell.getValue(cellRow, cellCol))[0:1] == '=':
                    # if it should have a formula but doesn't, it failed to
                    # parse
                    existingOutput = 'SYNTAX-ERROR'
                else:
                    existingOutput = None
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
            self.appendChartChild(self.charts[i])

        # preview -- do this before headers/siders so it's easy to insert before
        previewY = (1 + self.numRows) * self.rowHeight
        self.appendChild(UICell('preview', 0, previewY, placeholder='',
                                width=self.getWidth(), height=self.rowHeight,
                                fill='white', editable=False, visibleChars=155))

        # UI scaffolding: cover the corner and ensure right line stays
        self.appendChild(Rectangle('hider', 0, 0, width=self.siderWidth,
                                   height=self.rowHeight, fill='white',
                                   borderColor=''))
        self.appendChild(Line('right-line', self.getWidth(), 0,
                              angle=90, length=self.getHeight()))

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

        self.makeKeyListener()

    # called by text field after new value entered
    # NOTE: this might be called by a selected-but-not-active cell,
    #       so ALWAYS use sender instead of (possibly-None) self.activeCell
    def saveCell(self, sender):
        row, col = self.absRowColFromCellName(sender.name)

        if sender.text == '':
            Cell.delete(row, col)
            sender.setOutputText(None)
        else:
            try:
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
        cell = self.getChildForAbsRowCol(row, col)
        cell.setOutputText(str(Cell.getValue(row, col)))
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
        # include headers and preview
        return (2 + self.numRows) * self.rowHeight

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
                child = self.getChildForAbsRowCol(depRef.row, depRef.col)
                child.highlight('orange')
                self.highlighted.append(child)

    def setSelectedCells(self, sender, modifier):
        if self.activeCell and self.activeCell is not sender:
            self.activeCell.finishEditing()

        if (modifier is not None  # only allow modifiers for non-header/siders
                and len(self.selectedCells) > 0
                and sender.name[0] != 'H' and sender.name[0] != 'S'):
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

            if sender.name[0] == 'H' or sender.name[0] == 'S':  # whole row/col
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
        if len(self.selectedCells) == 0:
            return
        pivotCell = self.selectedCells[0]
        self.deselectAllCellsButSender(sender, startIndex=1)
        self.selectedCells = [pivotCell]
        pivRow, pivCol = SpreadsheetGrid.rowColFromCellName(
            pivotCell.name)
        selRow, selCol = SpreadsheetGrid.rowColFromCellName(sender.name)
        # we need to select from pivot to sel so that the original (i.e., user)
        # selection order is preserved
        # use "row adjustment" to ensure we're inclusive on the "upper" bound
        if pivRow > selRow:
            rowStep = -1
            rowAdj = -1
        else:
            rowStep = +1
            rowAdj = +1

        if pivCol > selCol:
            colStep = -1
            colAdj = -1
        else:
            colStep = +1
            colAdj = +1

        for row in range(pivRow, selRow + rowAdj, rowStep):
            for col in range(pivCol, selCol + colAdj, colStep):
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
        preview = self.getChild('preview')
        if len(self.selectedCells) == 0:
            preview.setText('')
        elif len(self.selectedCells) == 1:
            selectedRow, selectedCol = self.absRowColFromCellName(
                self.selectedCells[0].name)
            preview.setText(Cell.getRaw(selectedRow, selectedCol))
        else:
            selectedCellRefs = [CellRef(*self.absRowColFromCellName(cell.name))
                                for cell in self.selectedCells]
            summaryText = ''

            count = Formula(Operator.get('COUNT'), selectedCellRefs)
            sumVal = Formula(Operator.get('SUM'), selectedCellRefs)
            mean = Formula(Operator.get('AVERAGE'), selectedCellRefs)
            mode = Formula(Operator.get('MODE'), selectedCellRefs)
            minVal = Formula(Operator.get('MIN'), selectedCellRefs)
            maxVal = Formula(Operator.get('MAX'), selectedCellRefs)
            for formula in [count, sumVal, mean, mode, minVal, maxVal]:
                try:
                    res = formula.evaluate()
                    summaryText += (formula.operator.name + '='
                                    + str(res) + '   ')
                except:
                    pass
            preview.setText(summaryText[:-1])  # ignore trailing space
            pass

    def onKeypress(self, event):
        arrowDir = Direction.fromKey(event.key)
        if arrowDir:
            drow, dcol = arrowDir.value
            if event.optionDown:
                nextRow, nextCol = self.curTopRow + drow, self.curLeftCol + dcol
                if self.isLegalScrollPos(nextRow, nextCol):
                    self.scroll(arrowDir)
            else:
                self.navigate(arrowDir, blockSelect=event.shiftDown)
        elif event.key == 'i' and event.commandDown:
            self.startImport()
        elif event.key == 'l' and event.commandDown:
            self.insertChart(ChartType.LINE)
        elif event.key == 't' and event.commandDown:
            self.insertChart(ChartType.SCATTER)
        elif event.key == 'p' and event.commandDown:
            self.insertChart(ChartType.PIE)
        elif event.key == 'b' and event.commandDown:
            self.insertChart(ChartType.BAR)
        elif event.key == 'r' and event.commandDown:
            self.transposeSelection()

    def navigate(self, arrowDir, blockSelect=False):
        if self.selectedCells == []:
            return
        drow, dcol = arrowDir.value
        if blockSelect:
            prevSelection = self.selectedCells[-1]
        else:
            prevSelection = self.selectedCells[0]
        prevRow, prevCol = SpreadsheetGrid.rowColFromCellName(
            prevSelection.name)
        nextRow, nextCol = prevRow + drow, prevCol + dcol

        # NOTE: we only clear all selected AFTER we verify legality
        if 0 <= nextRow < self.numRows and 0 <= nextCol < self.numCols:
            # if the cell is on screen, just move to it
            if blockSelect:
                # hacky, but it works
                self.blockSelect(self.getChild(f'{nextRow},{nextCol}'))
            else:
                self.deselectAllCellsButSender(None)  # clear old selection
                self.getChild(f'{nextRow},{nextCol}').select()
        else:
            # if the cell is off-screen, make sure it's legal and scroll
            scrollRow = self.curTopRow + drow
            scrollCol = self.curLeftCol + dcol
            if self.isLegalScrollPos(scrollRow, scrollCol):
                if blockSelect:
                    self.scroll(arrowDir)
                    self.blockSelect(self.getChild(prevSelection.name))
                else:
                    self.deselectAllCellsButSender(None)  # clear old selection
                    self.scroll(arrowDir)
                    self.getChild(prevSelection.name).select()
            elif len(self.selectedCells) > 1 and not blockSelect:
                # standard behavior is to reduce selection to 1
                self.deselectAllCellsButSender(self.selectedCells[0])

    def isLegalScrollPos(self, row, col):
        return 0 <= row and 0 <= col < 26 - self.numCols + 1

    # transposes the currently selected region (filling in the smallest
    # rectangular region containing all currently selected cells)
    def transposeSelection(self):
        if len(self.selectedCells) == 0:
            return
        cols, colRefs = self.getSelectedColumnRefs()
        upperLeft = colRefs[cols[0]][0]
        numRows = max([len(colRefs[col]) for col in cols])
        numCols = len(cols)
        squareSize = max(numRows, numCols)

        oldValues = {}
        for row in range(numRows):
            for col in range(numCols):
                absRow = upperLeft.row + row
                absCol = upperLeft.col + col
                oldValues[absRow, absCol] = Cell.getRaw(absRow, absCol)

        for row in range(squareSize):
            for col in range(squareSize):
                # Don't wipe out cells that aren't in orig OR transpose
                if (row < numRows and col < numCols) or\
                        (row < numCols and col < numRows):
                    srcRow = upperLeft.row + row
                    srcCol = upperLeft.col + col
                    trgRow = upperLeft.row + col
                    trgCol = upperLeft.col + row
                    # swap transposed cells, or clear out ones that were
                    # part of the original but aren't part of the transpose
                    cellToUpdate = self.getChildForAbsRowCol(trgRow, trgCol)
                    newVal = oldValues.get((srcRow, srcCol), '')
                    # this does error handling, dependency updating, etc. for us
                    # note, however, that it assumes the cell has already
                    # re-rendered, so we'll have to do that manually afterward
                    cellToUpdate.setText(newVal)
                    cellToUpdate.rerender()

    def startImport(self):
        if len(self.selectedCells) == 0:
            return

        target = self.selectedCells[0]
        self.deselectAllCellsButSender(None)
        importer = WebImporter(
            onImport=lambda table, target=target:
            self.importWebTable(table, target))
        self.runModal(importer)

    def importWebTable(self, table: Table, targetCell):
        numLetteredCols = 26
        selRow, selCol = self.absRowColFromCellName(targetCell.name)
        if selCol + table.longestRowLength >= numLetteredCols:
            return False

        curRow, curCol = selRow, selCol
        for row in table.rows:
            for cell in row:
                text = cell  # Tables want to be immutable
                while len(text) > 0 and text[0] == '=':
                    # No arbitrary code execution!
                    text = text[1:]
                Cell.setRaw(curRow, curCol, text)  # safe b/c no formulae
                if self.absPosIsVisible(curRow, curCol):
                    uiCell = self.getChildForAbsRowCol(curRow, curCol)
                    uiCell.setOutputText(None)
                    uiCell.setText(text)
                curCol += 1
            curRow += 1
            curCol = selCol
        return True

    # returns a tuple of the currently selected column indices (absolute,
    # in order) and a dictionary mapping those indices to CellRefs to the
    # selected cells in each column
    def getSelectedColumnRefs(self):
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

        return cols, colRefs


    def insertChart(self, chartType: ChartType):
        if len(self.selectedCells) == 0:
            return
        cols, colRefs = self.getSelectedColumnRefs()

        upperLeftValue = str(colRefs[cols[0]][0].getValue())
        if upperLeftValue.isdigit():
            useTitles = False
        else:
            useTitles = True
            # Being able to have pie charts without titles is fairly useless
            # and certainly much more of a headache than it's worth -- leaving
            # here just in case, though
            # if chartType == ChartType.PIE:
            #     firstCol = colRefs[cols[0]]
            #     if len(firstCol) > 1:
            #         nextPossibleHeader = str(firstCol[1].getValue())
            #         # if the first dep col has a header, assume they all do
            #         if nextPossibleHeader.isdigit():
            #             depTitles = False

        indSeries = None
        depSeries = []
        titles = []
        for i in range(len(cols)):
            if useTitles:
                title = colRefs[cols[i]][0]
                data = colRefs[cols[i]][1:]
                series = Series(title, data)
                titles.append(str(title.getValue()))
            else:
                data = colRefs[cols[i]]
                series = Series(None, data)

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
        data = ChartData(ident, chartType, defaultTitle, indSeries, depSeries,
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
        x, y = self.getChartCoords(chartData)

        # Idea of map of callables in lieu of switch statement from:
        # https://jaxenter.com/implement-switch-case-statement-python-138315.html
        chartTypeMap = {
            ChartType.PIE: PieChart,
            ChartType.LINE: LineChart,
            ChartType.SCATTER: ScatterChart,
            ChartType.BAR: BarChart
        }
        # TODO: We can simplify this and other event methods significantly
        #       by simply passing identifiers from the caller
        self.appendBefore(chartTypeMap[chartData.chartType](
            f'chart{chartData.ident}',
            x, y, data=chartData,
            onDelete=lambda ident=chartData.ident: self.deleteChart(ident),
            onConfigure=lambda: self.deselectAllCellsButSender(None),
            onMove=self.moveChart), 'preview')

    def getChartCoords(self, chartData):
        x = ((chartData.col - self.curLeftCol) * self.colWidth) \
            + self.siderWidth
        y = ((chartData.row - self.curTopRow) + 1) * self.rowHeight
        return x, y

    def deleteChart(self, ident):
        self.removeChild(f'chart{ident}')
        i = 0
        while i < len(self.charts):
            if self.charts[i].ident == ident:
                self.charts.pop(i)
                return
            i += 1

    def moveChart(self, sender, coords):
        # hackily account for the fact that events propagate down rather than up
        self.deselectAllCellsButSender(None)

        i = 0
        while i < len(self.charts):
            if self.charts[i].ident == sender.props['data'].ident:
                self.charts[i].row, self.charts[i].col = coords
                # ACK! We're breaking the #1 rule here (components should never
                # need to know their own position on screen), but I can't think
                # of a better way to do this.
                relCoords = self.getChartCoords(self.charts[i])
                sender.x = int(relCoords[0] + self.x)
                sender.y = int(relCoords[1] + self.y)
                return
            i += 1

    def onClick(self, event):
        self.dragStartX = event.x
        self.dragStartY = event.y

    def onDrag(self, event):
        x, y = event.x, event.y

        if (abs(x - self.dragStartX) < self.dragThreshold
                and abs(y - self.dragStartY) < self.dragThreshold):
            # avoid being too sensitive
            return

        row = int((y - self.rowHeight) / self.rowHeight)
        col = int((x - self.siderWidth) / self.colWidth)
        if 0 <= row < self.numRows and 0 <= col < self.numCols:
            # This is a bit hacky, but we're just doing block select!
            self.blockSelect(self.getChild(f'{row},{col}'))
            # If we later change block select not to reselect sender,
            # we could equivalently do:
            # self.getChild(f'{row},{col}').select(modifier='Shift')

    # reloads the grid, fetching cells from Cell and replacing charts with
    # those specified
    def reload(self, charts):
        # Note: this is ESSENTIAL, or old cells won't resign their key listener
        # status, making them zombies that hog memory and ruin interaction
        self.deselectAllCellsButSender(None)
        self.selectedCells = []
        self.highlighted = []
        self.activeCell = None
        self.curLeftCol = 0
        self.curTopRow = 0
        self.charts = charts
        self.removeAllChildren()
        self.initChildren()

    # returns the child cell for an absolute cell position, or None if
    # the specified cell is not currently on screen
    def getChildForAbsRowCol(self, row, col):
        relRow, relCol = self.relRowColFromAbs(row, col)
        return self.getChild(f'{relRow},{relCol}')

    # returns the relative position of an absolute cell location
    def relRowColFromAbs(self, row, col):
        return row - self.curTopRow, col - self.curLeftCol

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

class Direction(Enum):
    RIGHT = (0, 1)
    LEFT = (0, -1)
    UP = (-1, 0)
    DOWN = (1, 0)

    @staticmethod
    def fromKey(keyStr):
        upper = keyStr.upper()
        if upper in Direction.__members__:
            return Direction[upper]
        elif upper == 'TAB':
            return Direction.RIGHT
        else:
            return None
