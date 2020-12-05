# ChartConfiguration.py
# Joseph Rotella (jrotella, F0)
#
# Contains the modal chart configuration UI view.
from modular_graphics.atomic_elements import Text
from modular_graphics.input_elements import TextField, Button
from modular_graphics.modal import ModalView


class ChartConfiguration(ModalView):
    def __init__(self, **props):
        super().__init__(props)
        self.width = 400
        self.height = 485
        self.rowHeight = 40
        self.headerY = 20
        self.col1Start = (10, self.headerY + self.rowHeight)
        self.col2Start = (215, self.headerY + 2 * self.rowHeight)
        self.titleFieldWidth = 305
        self.labelWidth = 50
        self.longLabelWidth = 245
        self.buttonWidth = 100
        if 'data' not in self.props or 'onDelete' not in self.props:
            raise Exception('Missing required props for chart configurator')

    def initChildren(self):
        chartData = self.props['data']
        xMin = str(chartData.xMin) if chartData.xMin is not None else 'auto'
        xMax = str(chartData.xMax) if chartData.xMax is not None else 'auto'
        yMin = str(chartData.yMin) if chartData.yMin is not None else 'auto'
        yMax = str(chartData.yMax) if chartData.yMax is not None else 'auto'
        title = chartData.title

        # header
        self.appendChild(Text('header', self.width // 2, self.headerY,
                              text='Chart Configuration',
                              font='"Andale Mono" 14', anchor='center'))

        # title
        col1X, col1Y = self.col1Start
        self.addPairedField(col1X, col1Y, 'title', 'title', title,
                            width=self.titleFieldWidth, chars=40)
        col1Y += self.rowHeight

        # column 1
        self.addPairedField(col1X, col1Y, 'xmin', 'x min', xMin)
        col1Y += self.rowHeight
        self.addPairedField(col1X, col1Y, 'ymin', 'y min', yMin)
        col1Y += self.rowHeight

        # column 2
        col2X, col2Y = self.col2Start
        self.addPairedField(col2X, col2Y, 'xmax', 'x max', xMax)
        col2Y += self.rowHeight
        self.addPairedField(col2X, col2Y, 'ymax', 'y max', yMax)

        depSeries = chartData.dependentSeries
        for i in range(len(depSeries)):
            color = depSeries[i].color
            title = depSeries[i].title
            self.addPairedField(col1X, col1Y, f'color{i}',
                                f'series {i} ({title}) color', color,
                                longLabel=True)
            col1Y += self.rowHeight

        self.appendChild(Button('delete-button',
                                (self.width - self.buttonWidth) // 2,
                                col1Y, width=self.buttonWidth,
                                text='Delete Chart',
                                action=self.onDelete))
        col1Y += self.rowHeight

        self.appendChild(Button('save-button',
                                (self.width - self.buttonWidth) // 2,
                                col1Y, width=self.buttonWidth,
                                text='Save Changes',
                                action=self.onSave))

    def addPairedField(self, x, y, name, label, text, width=None, chars=None,
                       longLabel=False):
        textX, textY = x, y + 10
        fieldX, fieldY = x + self.labelWidth, y
        if longLabel:
            fieldX = x + self.longLabelWidth
        self.appendChild(Text(f'{name}-label', textX, textY,
                              text=label, anchor='w'))
        extraArgs = {}
        if width is not None:
            extraArgs['width'] = width
        if chars is not None:
            extraArgs['visibleChars'] = chars
        self.appendChild(TextField(name, fieldX, fieldY, text=text,
                                   placeholder=None, **extraArgs))

    def onSave(self, _):
        chartData = self.props['data']

        xMin = self.getChild('xmin').text
        xMax = self.getChild('xmax').text
        yMin = self.getChild('ymin').text
        yMax = self.getChild('ymax').text

        title = self.getChild('title').text
        chartData.title = title

        try: xMin = int(xMin)
        except: xMin = None
        chartData.xMin = xMin

        try: xMax = int(xMax)
        except: xMax = None
        chartData.xMax = xMax

        try: yMin = int(yMin)
        except: yMin = None
        chartData.yMin = yMin

        try: yMax = int(yMax)
        except: yMax = None
        chartData.yMax = yMax

        i = 0
        while self.hasChild(f'color{i}'):
            chartData.dependentSeries[i].color = self.getChild(f'color{i}').text
            i += 1

        self.dismiss()

    def onDelete(self, _):
        self.props['onDelete']()
        self.dismiss()

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
