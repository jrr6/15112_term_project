from data_visualization.ChartData import ChartData
from modular_graphics import UIElement, RelativeCanvas

class BarChart(UIElement):

    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)

        self.kTitleFont = '"Andale Mono" 14'
        self.kSideMargin = 10
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
        self.kGraphTopY = 50
        self.kGraphWidth = 500
        self.kGraphHeight = 400
        self.kGraphBotY = self.kGraphTopY + self.kGraphHeight
        self.kSideLabelsWidth = 30
        self.kIntraGroupMargin = 2
        self.kInterGroupMargin = 10
        self.kGraphStartX = self.kSideLabelsWidth + self.kSideMargin

        if 'data' not in props or not isinstance(self.props['data'], ChartData):
            raise Exception('Invalid or missing data passed to BarChart.')

    def draw(self, canvas: RelativeCanvas):
        from formulae import CellRef
        chartData: ChartData = self.props['data']
        canvas.createRectangle(0, 0, self.getWidth(), self.getHeight(),
                               fill='white')

        # chart title
        canvas.createText(self.getWidth() // 2, self.kTopMargin,
                          text=chartData.title, anchor='n',
                          font=self.kTitleFont)

        # TODO: Move this to a ChartUtils file -- we'll need it for others
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

        # SAVE THIS FOR LATER -- for now, we get the bounds fed to us :)
        # maxVal = max([val.getValue() if isinstance(val, CellRef) else val
        #               for series in chartData.dependentSeries
        #               for val in series.data])

        # labels
        indData = chartData.independentSeries.data
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
                colHeight = ((depSeries.data[i] / chartData.yMax)
                             * self.kGraphHeight)

                canvas.createRectangle(startX, self.kGraphBotY, endX,
                                       self.kGraphBotY - colHeight,
                                       fill=depSeries.color,
                                       width=0)

            # category label
            if isinstance(indData[i], CellRef):
                text = str(indData[i].getValue())
            else:
                text = str(indData[i])
            canvas.createText(curX + indVarBucketWidth / 2,
                              self.kGraphBotY + self.kEdgeLabelMargin,
                              text=text, anchor='n')
            curX += indVarBucketWidth

    def getWidth(self):
        return self.kGraphStartX + self.kGraphWidth + self.kSideMargin

    def getHeight(self):
        textHeight = 15  # approximation of bottom label height
        return self.kGraphBotY + textHeight + self.kBottomMargin
