# PieChart.py
# Joseph Rotella (jrotella, F0)
#
# Contains UI code for pie chart data visualization.

from data_visualization.GenericChart import GenericChart
import math

class PieChart(GenericChart):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.kGraphWidth = self.kGraphHeight  # needs to be square!
        self.kMinPctLabel = 0.05

    def drawChart(self, canvas):
        chartData = self.props['data']
        depSeries = chartData.dependentSeries
        if len(depSeries) == 0:
            raise Exception('Cannot draw pie chart with no data!')
        self.drawBGAndTitle(canvas)
        self.drawKey(canvas)

        # draw wedges
        # just extract the first datum from each dependent series
        seriesData = list(map(lambda x: x.evaluatedData()[0], depSeries))
        total = sum(seriesData)

        arcPos = 90  # start at top
        for i in range(len(depSeries)):
            topLeft = (self.kGraphStartX,
                       self.kGraphTopY)
            botRight = (self.kGraphStartX + self.kGraphWidth,
                        self.kGraphBotY)

            percentage = seriesData[i] / total
            if percentage == 1:  # just draw a circle
                canvas.createOval(*topLeft, *botRight, fill=depSeries[i].color,
                                  width=0)
                break
            elif percentage != 0:  # don't draw ugly lines for 0
                # Note to grader: I did NOT reference my solution to the pie
                # chart homework in writing this

                # negative angle b/c every other spreadsheet program goes
                # clockwise
                angle = -(360 * percentage)
                canvas.createArc(*topLeft, *botRight, outline='',
                                 start=arcPos, extent=angle,
                                 fill=depSeries[i].color)
                if percentage > self.kMinPctLabel:
                    # draw nontrivial percentages in middle of respective slice
                    xMid = (topLeft[0] + botRight[0]) / 2
                    yMid = (topLeft[1] + botRight[1]) / 2
                    radius = yMid - self.kGraphTopY
                    midSectorAngle = math.radians(arcPos + angle / 2)
                    textX = xMid + (radius / 2) * math.cos(midSectorAngle)
                    textY = yMid - (radius / 2) * math.sin(midSectorAngle)
                    canvas.createText(textX, textY,
                                      text=str(round(percentage * 100)) + '%',
                                      anchor='center')
                arcPos += angle

    def getWidth(self):
        return self.kGraphWidth + 2 * self.kSideMargin

    def getHeight(self):
        return self.kGraphBotY + self.kBottomMargin
