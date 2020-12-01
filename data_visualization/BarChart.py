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
        self.kSideLabelMargin = 2

        # graph constants
        self.kGraphTopY = 50
        self.kGraphWidth = 500
        self.kGraphHeight = 400
        self.kGraphBotY = self.kGraphTopY + self.kGraphHeight
        self.kLabelsWidth = 20
        self.kIntraGroupMargin = 2
        self.kInterGroupMargin = 10
        self.kGraphStartX = self.kLabelsWidth + self.kSideMargin + 5  # margin

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
                                   fill=depSeries.color)
            textX = curKeyX + self.kKeyBlockSize + self.kKeyPadding
            textYFudgeFactor = -1
            canvas.createText(textX, self.kKeyY + textYFudgeFactor,
                              text=depSeries.title, anchor='nw')
            curKeyX += self.kKeyItemWidth

        # side labels
        for i in range(5):
            canvas.createText(self.kGraphStartX - self.kSideLabelMargin,
                              self.kGraphBotY - i * self.kGraphHeight / 4,
                              text=str((i / 4) * chartData.yMax),
                              anchor='e')

        # SAVE THIS FOR LATER -- for now, we get the bounds fed to us :)
        # maxVal = max([val.getValue() if isinstance(val, CellRef) else val
        #               for series in chartData.dependentSeries
        #               for val in series.data])

        # labels
        indData = chartData.independentSeries.data
        curX = self.kGraphStartX
        indVarBucketWidth = self.kGraphWidth / len(indData)
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
                                       fill=depSeries.color)

            # category label
            if isinstance(indData[i], CellRef):
                text = str(indData[i].getValue())
            else:
                text = str(indData[i])
            canvas.createText(curX + indVarBucketWidth / 2,
                              self.kGraphBotY,
                              text=text, anchor='n')
            curX += indVarBucketWidth

    def getWidth(self):
        return self.kGraphStartX + self.kGraphWidth + self.kSideMargin

    def getHeight(self):
        return self.kGraphBotY + self.kBottomMargin * 2  # room for labels
