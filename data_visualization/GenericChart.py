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
        self.kSideLabelsWidth = 30
        self.kGraphStartX = self.kSideMargin
        self.kGraphTopY = 50
        self.kGraphWidth = 500
        self.kGraphHeight = 400
        self.kGraphBotY = self.kGraphTopY + self.kGraphHeight
        self.kBottomLabelsHeight = 15

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
