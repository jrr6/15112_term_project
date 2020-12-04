# Chart.py
# Joseph Rotella (jrotella, F0)
#
# Represents a chart model object.
import random
from enum import Enum
from typing import Union


class Series:
    def __init__(self, titleRef, data: list, color: Union[str, None]=None):
        self._titleRef = titleRef
        self._data = data  # callers should just use `evaluated` methods
        self.color = color  # only required for dependent series

    @property
    def title(self):
        return self._titleRef.getValue()

    def dataLength(self):
        return len(self._data)

    def evaluatedData(self):
        from formulae import CellRef
        res = []
        for datum in self._data:
            if isinstance(datum, CellRef):
                res.append(datum.getValue())
            else:
                res.append(datum)
        return res

    def evaluatedDatum(self, index):
        from formulae import CellRef
        if isinstance(self._data[index], CellRef):
            return self._data[index].getValue()
        else:
            return self._data[index]

class ChartType(Enum):
    BAR = 0
    SCATTER = 1
    LINE = 2
    PIE = 3

class ChartData:
    def __init__(self, ident: int, chartType: ChartType, title: str,
                 independentSeries: Series, dependentSeries: list[Series],
                 xMin: Union[float, None], xMax: Union[float, None],
                 yMin: Union[float, None], yMax: Union[float, None],
                 row: int, col: int, autocolor=False):
        self.ident = ident
        self.chartType = chartType
        self.title = title
        self.independentSeries = independentSeries
        self.dependentSeries = dependentSeries
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.row = row
        self.col = col
        if autocolor:
            self.assignRandomColors()

    def assignRandomColors(self):
        colors = ['red', 'orange', 'yellow', 'blue', 'green', 'cyan', 'pink',
                  'green yellow', 'midnight blue', 'purple', 'thistle']
        for i in range(len(self.dependentSeries)):
            self.dependentSeries[i].color = \
                colors.pop(random.randint(0, len(colors) - 1))
