# Chart.py
# Joseph Rotella (jrotella, F0)
#
# Represents a chart model object.
from enum import Enum
from typing import Union


class Series:
    def __init__(self, title: str, data: list, color: Union[str, None]=None):
        self.title = title
        # NOTE: data is going to need some sort of ref capability!
        self.data = data
        self.color = color  # only required for dependent series

class ChartType(Enum):
    BAR = 0
    SCATTER = 1
    LINE = 2
    PIE = 3

class ChartData:
    def __init__(self, chartType: ChartType, title: str,
                 independentSeries: Series, dependentSeries: list[Series],
                 xMin: Union[float, None], xMax: Union[float, None],
                 yMin: Union[float, None], yMax: float):
        self.chartType = chartType
        self.title = title
        self.independentSeries = independentSeries
        self.dependentSeries = dependentSeries
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax

