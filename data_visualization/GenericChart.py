from data_visualization.ChartData import ChartData
from modular_graphics import UIElement


class GenericChart(UIElement):
    def __init__(self, name, x, y, props):
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
        self.kGraphStartX = self.kSideMargin
        self.kGraphTopY = 50
        self.kGraphWidth = 500
        self.kGraphHeight = 400
        self.kGraphBotY = self.kGraphTopY + self.kGraphHeight

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

