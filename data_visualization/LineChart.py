# LineChart.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI code for the line chart type.
from data_visualization.GenericChart import GenericChart


class LineChart(GenericChart):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.kGraphStartX += self.kSideLabelsWidth  # since we have text

    def drawChart(self, canvas):
        self.drawBGAndTitle(canvas)
        self.drawKey(canvas)
        self.drawSideLabels(canvas)
        self.drawBottomLabels(canvas)
        self.plotData(canvas, linear=True)

    def getWidth(self):
        return self.getLabeledChartWidth()

    def getHeight(self):
        return self.getLabeledChartHeight()
