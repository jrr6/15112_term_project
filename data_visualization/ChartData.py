# Chart.py
# Joseph Rotella (jrotella, F0)
#
# Represents a chart model object.
import random
from enum import Enum
from typing import Union

from formulae import CellRef
from utils import splitEscapedString


class Series:
    from formulae import CellRef

    def __init__(self, titleRef, data: list[CellRef],
                 color: Union[str, None]=None):
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
        else:  # this is for debugging and shouldn't be reached in production
            return self._data[index]

    def serialize(self):
        result = f'{self._titleRef.serialize()},'
        if self.color is not None and ',' not in self.color:
            result += f'{self.color}'
        result += ','
        for ref in self._data:
            result += ref.serialize() + ','
        result = result[:-1]
        return result

    @staticmethod
    def deserialize(data):
        entities = data.split(',')
        titleRef = CellRef.deserialize(entities[0])
        color = entities[1] if entities[1] != '' else None
        data = []
        for entity in entities[2:]:
            data.append(CellRef.deserialize(entity))
        return Series(titleRef, data, color)


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

    def serialize(self):
        from SpreadsheetScene import SpreadsheetScene
        # NOTE: we need to ensure no serialized sub-entity contains unescaped
        #       pipes

        # Replace the delimeter used by SpreadsheetApp so it doesn't need to
        title = self.title.replace('|', '\\|')\
            .replace(SpreadsheetScene.kChartDelimiter, '')
        xMin = str(self.xMin) if self.xMin is not None else ''
        xMax = str(self.xMax) if self.xMax is not None else ''
        yMin = str(self.yMin) if self.yMin is not None else ''
        yMax = str(self.yMax) if self.yMax is not None else ''

        indepSeries = self.independentSeries.serialize()  # only `|`, `,` and #s
        depSeries = ''
        for series in self.dependentSeries:
            depSeries += series.serialize() + '|'
        depSeries = depSeries[:-1]

        return f'{self.ident}|{self.chartType.value}|{self.row}|{self.col}|'\
               f'{xMin}|{xMax}|{yMin}|{yMax}|{title}|{indepSeries}|{depSeries}'

    @staticmethod
    def deserialize(data):
        if data == '':
            return
        entities = splitEscapedString(data, '|')
        ident = entities[0]
        type = ChartType(int(entities[1]))
        row = int(entities[2])
        col = int(entities[3])
        xMin = int(entities[4]) if entities[4] != '' else None
        xMax = int(entities[5]) if entities[5] != '' else None
        yMin = int(entities[6]) if entities[6] != '' else None
        yMax = int(entities[7]) if entities[7] != '' else None
        title = entities[8].replace('\\|', '|')
        indepSeries = Series.deserialize(entities[9])
        # everything else in dependent series
        depSeries = [Series.deserialize(seriesData)
                     for seriesData in entities[10:]]
        return ChartData(ident, type, title, indepSeries, depSeries, xMin, xMax,
                         yMin, yMax, row, col)
