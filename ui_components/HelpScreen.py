# HelpScreen.py
# Joseph Rotella (jrotella, F0)
#
# Contains code for help screen modal UI.
from modular_graphics.atomic_elements import Text
from modular_graphics.modal import ModalView


class HelpScreen(ModalView):
    def __init__(self, **props):
        super().__init__(props)
        self.height = 600
        self.width = 700
        self.kDrawStartY = 10
        self.kMargin = 10
        self.kStepY = 20

    def initChildren(self):
        curY = self.kDrawStartY
        self.appendChild(Text('header', self.width // 2, curY,
                              text='SimpleSheets Help',
                              font='"Andale Mono" 14', anchor='center'))
        curY += 25

        self.appendChild(Text(
            'text', self.kMargin, curY, width=self.width - 2 * self.kMargin,
            anchor='nw',
            text='Welcome to SimpleSheets! This Help Guide will introduce you to a few of the app\'s key features.\n\n'
                 'To insert text, double-click a cell, or select a cell and press Return. When a cell is active, it will '
                 'become highlighted. Additionally, you can click to select cells, and drag-, Shift-, or Command-click to select '
                 'multiple. Click on a row or column label to quickly select all visible cells in that row or column. When you select '
                 'a cell, its full contents will appear in the preview bar at the bottom. If you select multiple, you\'ll see useful '
                 'contextual information appear in the preview bar.\n\n'
                 'Navigate cells by clicking or using the arrow keys. To scroll the entire spreadsheet, hold Option and press the arrow '
                 'keys. To select cells with the keyboard, hold Shift while navigating.\n\n'
                 'To save a file, click Save and enter a path. Paths can be absolute or relative to the working directory, '
                 'and SimpleSheets will automatically create any directories in the path that don\'t exist. To open a file, '
                 'click Open and enter the path of an existing file. To create a new file, click the New button in the toolbar.\n\n'
                 'Each file can contain multiple spreadsheets. Simply click the + button in the spreadsheet bar to create '
                 'a new sheet, or double-click a sheet to rename or delete it.\n\n'
                 'Cells can automatically compute values using formulas. To enter a formula, simply enter = as the first character in '
                 'a cell, then enter the formula. Formulas are written as functions, with cells or values passed as parameters. You can '
                 'also pass a block of cells using colon syntax (e.g., A1:C2). If a cell\'s formula depends on another cell, the cell '
                 'will automatically update when the dependency is modified. Here\'s an example of a formula: =SUM(14, C3, AVERAGE(D5:E7)).\n\n'
                 'To create a chart, enter your data so that each variable is in its own column. '
                 'If your data is flipped, use the transpose tool to reorient it: drag-, Shift-, or Command-select your data, '
                 'then click Transpose. Once your data is correct, select your data by clicking and dragging '
                 'or Shift-selecting, and click a chart type to insert a chart. Once you\'ve inserted a chart, you can edit its '
                 'properties by double-clicking on it. Move charts by dragging them across the sheet.\n\n'
                 'To import data from the web, select the cell at which you\'d like to insert the data, then click the Web Import tool '
                 'in the toolbar (the magnifying glass). Enter the URL of a website with tabular data, then select the table you\'d '
                 'like to import. The data will automatically populate, starting with the selected cell as the upper left.\n\n'
                 'SimpleSheets also supports a robust set of keyboard shortcuts, which can be found in the README.'))
        curY += self.kStepY

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
