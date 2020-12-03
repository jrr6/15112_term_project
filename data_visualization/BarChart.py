from data_visualization.ChartData import ChartData
from data_visualization.GenericChart import GenericChart
from modular_graphics import RelativeCanvas

class BarChart(GenericChart):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)

        # label constants
        self.kEdgeLabelMargin = 2

        # graph constants
        self.kSideLabelsWidth = 30
        self.kIntraGroupMargin = 2
        self.kInterGroupMargin = 10
        self.kGraphStartX += self.kSideLabelsWidth  # since we have text

    def draw(self, canvas: RelativeCanvas):
        chartData: ChartData = self.props['data']
        self.drawBGAndTitle(canvas)
        self.drawKey(canvas)

        # I'm not sure we want a y-axis, but in case we ever do, here it is:
        # y axis
        # canvas.createLine(self.kGraphStartX, self.kGraphBotY,
        #                   self.kGraphStartX,
        #                   self.kGraphBotY - self.kGraphHeight,
        #                   fill='black')

        # side labels and gridlines
        for i in range(5):
            lineX = self.kGraphStartX
            textX = lineX - self.kEdgeLabelMargin
            y = self.kGraphBotY - i * self.kGraphHeight / 4
            axisLabel = str((i / 4) * chartData.yMax)
            canvas.createText(textX, y, text=axisLabel, anchor='e')
            canvas.createLine(lineX, y, lineX + self.kGraphWidth, y,
                              fill='black' if i == 0 else 'gray')

        # TODO: SAVE THIS FOR LATER -- for now, we get the bounds fed to us :)
        # maxVal = max([val.getValue() if isinstance(val, CellRef) else val
        #               for series in chartData.dependentSeries
        #               for val in series.data])

        # labels
        indData = chartData.independentSeries._data
        # give the first column intergroup margin-worth of padding
        curX = self.kGraphStartX + self.kInterGroupMargin
        indVarBucketWidth = ((self.kGraphWidth - self.kInterGroupMargin)
                             / len(indData))
        for i in range(len(indData)):
            # draw columns
            columnWidth = ((indVarBucketWidth - self.kInterGroupMargin)
                           / len(chartData.dependentSeries))
            for colIdx in range(len(chartData.dependentSeries)):
                depSeries = chartData.dependentSeries[colIdx]
                startX = curX + colIdx * columnWidth + self.kIntraGroupMargin
                endX = startX + columnWidth - 2 * self.kIntraGroupMargin
                # don't draw columns taller than 100% height
                colHeightPct = min(depSeries.evaluatedDatum(i) / chartData.yMax,
                                   1)
                colHeight = (colHeightPct * self.kGraphHeight)

                canvas.createRectangle(startX, self.kGraphBotY, endX,
                                       self.kGraphBotY - colHeight,
                                       fill=depSeries.color,
                                       width=0)

            # category label
            text = str(chartData.independentSeries.evaluatedDatum(i))
            canvas.createText(curX + indVarBucketWidth / 2,
                              self.kGraphBotY + self.kEdgeLabelMargin,
                              text=text, anchor='n')
            curX += indVarBucketWidth

    def getWidth(self):
        return self.kGraphStartX + self.kGraphWidth + self.kSideMargin

    def getHeight(self):
        textHeight = 15  # approximation of bottom label height
        return self.kGraphBotY + textHeight + self.kBottomMargin
