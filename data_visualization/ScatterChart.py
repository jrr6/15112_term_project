# ScatterChart.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI code for the scatter-plot chart.
from data_visualization.GenericChart import GenericChart

class ScatterChart(GenericChart):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.kGraphStartX += self.kSideLabelsWidth  # since we have text
        self.kDotRadius = 5

    @staticmethod
    def enumeratedSort(lst):
        indexedIterable = enumerate(lst)
        sortedWithIndices = sorted(indexedIterable, key=lambda x: x[1])
        sortedList = [x[1] for x in sortedWithIndices]
        indexList = [x[0] for x in sortedWithIndices]
        return indexList, sortedList

    def draw(self, canvas):
        chartData = self.props['data']

        self.drawBGAndTitle(canvas)
        self.drawKey(canvas)
        self.drawSideLabels(canvas)
        self.drawBottomLabels(canvas)

        indSeries = chartData.independentSeries
        depSeries = chartData.dependentSeries

        indData = indSeries.evaluatedData()
        # NOTE: we don't technically need enumdSort for scatter, but we WILL for line
        indexOrder, indData = ScatterChart.enumeratedSort(indData)
        for i in range(len(indData)):
            indVal = indData[i]
            if chartData.xMin <= indVal <= chartData.xMax:
                xPct = ((indVal - chartData.xMin) /
                        (chartData.xMax - chartData.xMin))
                xPos = self.kGraphStartX + xPct * self.kGraphWidth

                for j in range(len(depSeries)):
                    depSeriesIdx = indexOrder[i]
                    depDatum = depSeries[j].evaluatedDatum(depSeriesIdx)
                    if chartData.yMin <= depDatum <= chartData.yMax:
                        yPct = ((depDatum - chartData.yMin) /
                                (chartData.yMax - chartData.yMin))
                        yPos = self.kGraphBotY - yPct * self.kGraphHeight

                        canvas.createOval(xPos - self.kDotRadius,
                                          yPos - self.kDotRadius,
                                          xPos + self.kDotRadius,
                                          yPos + self.kDotRadius,
                                          outline='',
                                          fill=depSeries[j].color)

    def getHeight(self):
        return self.kGraphBotY + self.kBottomLabelsHeight + self.kBottomMargin

    def getWidth(self):
        return self.kGraphStartX + self.kGraphWidth + self.kSideMargin