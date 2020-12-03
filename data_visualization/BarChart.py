from data_visualization.ChartData import ChartData
from data_visualization.GenericChart import GenericChart
from modular_graphics import RelativeCanvas

class BarChart(GenericChart):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)

        # label constants
        self.kEdgeLabelMargin = 2

        # graph constants
        self.kIntraGroupMargin = 2
        self.kInterGroupMargin = 10
        self.kGraphStartX += self.kSideLabelsWidth  # since we have text

    def draw(self, canvas: RelativeCanvas):
        chartData: ChartData = self.props['data']
        self.drawBGAndTitle(canvas)
        self.drawKey(canvas)
        self.drawSideLabels(canvas, yMinOverride=0)

        # TODO: SAVE THIS FOR LATER -- for now, we get the bounds fed to us :)
        # maxVal = max([val.getValue() if isinstance(val, CellRef) else val
        #               for series in chartData.dependentSeries
        #               for val in series.data])

        # labels
        indDataLen = chartData.independentSeries.dataLength()
        # give the first column intergroup margin-worth of padding
        curX = self.kGraphStartX + self.kInterGroupMargin
        indVarBucketWidth = ((self.kGraphWidth - self.kInterGroupMargin)
                             / indDataLen)
        for i in range(indDataLen):
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
        return self.kGraphBotY + self.kBottomLabelsHeight + self.kBottomMargin
