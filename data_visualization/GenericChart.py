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
        yMin = yMinOverride if yMinOverride is not None \
            else self.props['data'].yMin
        yMax = yMaxOverride if yMaxOverride is not None \
            else self.props['data'].yMax

        for i in range(5):
            axisLabel = str(yMin + (i / 4) * (yMax - yMin))

            lineX = self.kGraphStartX
            textX = lineX - self.kEdgeLabelMargin
            y = self.kGraphBotY - i * self.kGraphHeight / 4
            canvas.createText(textX, y, text=axisLabel, anchor='e')
            canvas.createLine(lineX, y, lineX + self.kGraphWidth, y,
                              fill='black' if i == 0 else 'gray')

    def drawBottomLabels(self, canvas):
        xMin = self.props['data'].xMin
        xMax = self.props['data'].xMax
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

        for curSeries in depSeries:
            prevX, prevY = None, None
            for i in range(len(indData)):
                indVal = indData[i]
                depSeriesIdx = indexOrder[i]
                depDatum = curSeries.evaluatedDatum(depSeriesIdx)

                if indVal < chartData.xMin:
                    # we're still "before" the graph starts -- go to the next
                    continue
                elif indVal > chartData.xMax:
                    # we've gone off the graph -- we're done
                    break

                outOfBounds = not chartData.yMin <= depDatum <= chartData.yMax

                xPct = ((indVal - chartData.xMin) /
                        (chartData.xMax - chartData.xMin))
                if outOfBounds:
                    yPct = 0 if depDatum < chartData.yMin else 1
                else:
                    yPct = ((depDatum - chartData.yMin) /
                            (chartData.yMax - chartData.yMin))

                xPos = self.kGraphStartX + xPct * self.kGraphWidth
                yPos = self.kGraphBotY - yPct * self.kGraphHeight

                if linear:
                    # TODO: If the out-of-bounds is in the middle of data,
                    #       try to project the correct slope
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
                                          fill=depSeries[i].color)

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
