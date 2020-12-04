from data_visualization.ChartData import ChartData
from modular_graphics import UIElement


class GenericChart(UIElement):
    def __init__(self, name, x, y, props):
        super().__init__(name, x, y, props)

        self.kTitleFont = '"Andale Mono" 14'
        self.kSideMargin = 15
        self.kTopMargin = 5
        self.kBottomMargin = 10

        # key area constants
        self.kKeyY = 25
        self.kKeyBlockSize = 10
        self.kKeyPadding = 10
        self.kKeyTextWidth = 100
        self.kKeyItemWidth = self.kKeyBlockSize + self.kKeyPadding\
            + self.kKeyTextWidth

        # label constants
        self.kEdgeLabelMargin = 2

        # graph constants
        self.kDotRadius = 5
        self.kSideLabelsWidth = 30
        self.kGraphStartX = self.kSideMargin
        self.kGraphTopY = 50
        self.kGraphWidth = 500
        self.kGraphHeight = 400
        self.kGraphBotY = self.kGraphTopY + self.kGraphHeight
        self.kBottomLabelHeight = 15

        if 'data' not in props or not isinstance(self.props['data'], ChartData):
            raise Exception('Invalid or missing data passed to chart.')

    # Subclasses should use this method to draw so we can safely fail
    def drawChart(self, canvas):
        pass

    def draw(self, canvas):
        try:
            self.drawChart(canvas)
        except:
            self.drawBGAndTitle(canvas)  # cover up any partial drawing
            canvas.createText(self.getWidth() / 2, self.getHeight() / 2,
                              text='Data error', anchor='center')

    def drawBGAndTitle(self, canvas):
        canvas.createRectangle(0, 0, self.getWidth(), self.getHeight(),
                               fill='white')

        # chart title
        canvas.createText(self.getWidth() // 2, self.kTopMargin,
                          text=self.props['data'].title, anchor='n',
                          font=self.kTitleFont)

    def drawKey(self, canvas):
        chartData = self.props['data']
        # key
        keyAreaWidth = len(chartData.dependentSeries) * self.kKeyItemWidth
        curKeyX = self.getWidth() / 2 - keyAreaWidth / 2
        for depSeries in chartData.dependentSeries:
            # For debugging:
            # canvas.createRectangle(curKeyX, self.kKeyY,
            #                        curKeyX + self.kKeyItemWidth,
            #                        self.kKeyY + 15)
            canvas.createRectangle(curKeyX, self.kKeyY,
                                   curKeyX + self.kKeyBlockSize,
                                   self.kKeyY + self.kKeyBlockSize,
                                   width=0,  # hide border
                                   fill=depSeries.color)
            textX = curKeyX + self.kKeyBlockSize + self.kKeyPadding
            textYFudgeFactor = -1
            canvas.createText(textX, self.kKeyY + textYFudgeFactor,
                              text=depSeries.title, anchor='nw')
            curKeyX += self.kKeyItemWidth

    def drawSideLabels(self, canvas, yMinOverride=None, yMaxOverride=None):
        yMin, yMax = self.getYLimits()
        if yMinOverride is not None:
            yMin = yMaxOverride
        if yMaxOverride is not None:
            yMax = yMaxOverride

        for i in range(5):
            axisLabel = str(yMin + (i / 4) * (yMax - yMin))

            lineX = self.kGraphStartX
            textX = lineX - self.kEdgeLabelMargin
            y = self.kGraphBotY - i * self.kGraphHeight / 4
            canvas.createText(textX, y, text=axisLabel, anchor='e')
            canvas.createLine(lineX, y, lineX + self.kGraphWidth, y,
                              fill='black' if i == 0 else 'gray')

    def drawBottomLabels(self, canvas):
        xMin, xMax = self.getXLimits()
        for i in range(5):
            axisLabel = str(xMin + (i / 4) * (xMax - xMin))

            lineY = self.kGraphBotY
            textY = lineY + self.kEdgeLabelMargin
            x = self.kGraphStartX + i * self.kGraphWidth / 4
            canvas.createText(x, textY, text=axisLabel, anchor='n')
            canvas.createLine(x, lineY, x, lineY - self.kGraphHeight,
                              fill='black' if i == 0 else 'gray')

        graphCenter = self.kGraphStartX + self.kGraphWidth / 2
        canvas.createText(graphCenter,
                          self.kGraphBotY + self.kBottomLabelHeight,
                          anchor='n',
                          text=self.props['data'].independentSeries.title)

    def plotData(self, canvas, linear=False):
        chartData = self.props['data']
        indSeries = chartData.independentSeries
        depSeries = chartData.dependentSeries

        indData = indSeries.evaluatedData()
        indexOrder, indData = GenericChart.enumeratedSort(indData)

        xMin, xMax = self.getXLimits()
        yMin, yMax = self.getYLimits()

        for curSeries in depSeries:
            prevX, prevY = None, None
            for i in range(len(indData)):
                indVal = indData[i]
                depSeriesIdx = indexOrder[i]
                depDatum = curSeries.evaluatedDatum(depSeriesIdx)

                if indVal < xMin:
                    # we're still "before" the graph starts -- go to the next
                    continue
                elif indVal > xMax:
                    # we've gone off the graph -- we're done
                    break

                outOfBounds = not yMin <= depDatum <= yMax

                xPct = ((indVal - xMin) / (xMax - xMin))
                if outOfBounds:
                    yPct = 0 if depDatum < yMin else 1
                else:
                    yPct = ((depDatum - yMin) / (yMax - yMin))

                xPos = self.kGraphStartX + xPct * self.kGraphWidth
                yPos = self.kGraphBotY - yPct * self.kGraphHeight

                if linear:
                    # TODO: If the out-of-bounds is in the middle of data,
                    #       try to draw partial line segment with correct slope
                    if (prevX, prevY) != (None, None):
                        canvas.createLine(prevX, prevY, xPos, yPos,
                                          fill=curSeries.color)
                    if outOfBounds:
                        prevX = None
                        prevY = None
                    else:
                        prevX = xPos
                        prevY = yPos
                else:
                    if not outOfBounds:
                        canvas.createOval(xPos - self.kDotRadius,
                                          yPos - self.kDotRadius,
                                          xPos + self.kDotRadius,
                                          yPos + self.kDotRadius,
                                          outline='',
                                          fill=curSeries.color)

    @staticmethod
    def enumeratedSort(lst):
        indexedIterable = enumerate(lst)
        sortedWithIndices = sorted(indexedIterable, key=lambda x: x[1])
        sortedList = [x[1] for x in sortedWithIndices]
        indexList = [x[0] for x in sortedWithIndices]
        return indexList, sortedList

    def getLabeledChartHeight(self):
        return self.kGraphBotY + 2 * self.kBottomLabelHeight + self.kBottomMargin

    def getLabeledChartWidth(self):
        return self.kGraphStartX + self.kGraphWidth + self.kSideMargin

    def getXLimits(self):
        chartData = self.props['data']
        indData = chartData.independentSeries.evaluatedData()
        xMin = chartData.xMin if chartData.xMin is not None else min(indData)
        xMax = chartData.xMax if chartData.xMax is not None else max(indData)
        return self.ensureNonequalLimits(xMin, xMax)

    def getYLimits(self):
        chartData = self.props['data']
        autoMin = chartData.yMin is None
        autoMax = chartData.yMax is None
        yMin = chartData.yMin
        yMax = chartData.yMax

        if not autoMin and not autoMax:
            return self.ensureNonequalLimits(yMin, yMax)

        for series in chartData.dependentSeries:
            data = series.evaluatedData()
            curMin = min(data)
            curMax = max(data)
            if autoMin and (yMin is None or curMin < yMin):
                yMin = curMin
            if autoMax and (yMax is None or curMax > yMax):
                yMax = curMax

        return GenericChart.ensureNonequalLimits(yMin, yMax)

    @staticmethod
    def ensureNonequalLimits(self, lo, hi):
        if lo == hi:
            return lo, hi + 1
        return lo, hi
