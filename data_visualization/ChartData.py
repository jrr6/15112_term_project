# Chart.py
# Joseph Rotella (jrotella, F0)
#
# Represents a chart model object.
from enum import Enum
from typing import Union


class Series:
    def __init__(self, title: str, data: list, color: Union[str, None]=None):
        self.title = title
        self._data = data  # callers should just use `evaluated` methods
        self.color = color  # only required for dependent series

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
    def __init__(self, chartType: ChartType, title: str,
                 independentSeries: Series, dependentSeries: list[Series],
                 xMin: Union[float, None], xMax: Union[float, None],
                 yMin: Union[float, None], yMax: Union[float, None]):
        self.chartType = chartType
        self.title = title
        self.independentSeries = independentSeries
        self.dependentSeries = dependentSeries
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax

