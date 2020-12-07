# WebImporter.py
# Joseph Rotella (jrotella, F0)
#
# Contains the UI for the web scraper/importer to be displayed as a modal.
import requests
from bs4 import BeautifulSoup, element

from modular_graphics.atomic_elements import Text
from modular_graphics.input_elements import Button, TextField
from modular_graphics.modal import ModalView

class Table(object):
    def __init__(self, rows, name):
        self._rows = rows
        self._name = name

        self._longestRowLength = 0
        for row in self._rows:
            rowLen = len(row)
            if rowLen > self._longestRowLength:
                self._longestRowLength = rowLen

    # rows need to be immutable so computations remain correct
    @property
    def rows(self):
        return self._rows

    @property
    def name(self):
        return self._name

    @property
    def longestRowLength(self):
        return self._longestRowLength

    def getColDisplayWidths(self):
        cellWidths = []
        for row in self._rows:
            for colIdx in range(len(row)):
                cellText = row[colIdx]
                if len(cellWidths) <= colIdx:
                    cellWidths.append(len(cellText) + 5)
                elif cellWidths[colIdx] < len(cellText):
                    cellWidths[colIdx] = len(cellText) + 5
        return cellWidths

    def __str__(self):
        res = ''
        cellWidths = self.getColDisplayWidths()

        for row in self._rows:
            for cellIdx in range(len(row)):
                res += row[cellIdx].ljust(cellWidths[cellIdx])
            res += '\n'
        return res

class WebImporter(ModalView):
    def __init__(self, **props):
        super().__init__(props)
        self.width = 400
        self.height = 400
        if 'onImport' not in props:
            raise Exception('Attempt to construct WebImporter without handler.')

    def initChildren(self):
        margin = 10
        tfWidth = 200
        tfChars = 25
        tfHeight = 40
        buttonWidth = 50
        buttonHeight = tfHeight
        self.appendChild(TextField(
            'url-input', (self.getWidth() - tfWidth - buttonWidth) // 2, margin,
            height=tfHeight, width=tfWidth, visibleChars=tfChars,
            placeholder='Enter URL'
        ))
        self.appendChild(Button(
            'fetch-url', (self.getWidth() - buttonWidth + tfWidth) // 2, margin,
            text='Fetch', width=buttonWidth, height=buttonHeight,
            action=self._importTables
        ))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getInputURL(self):
        inputURL = self.getChild('url-input').text
        if inputURL.find('http://') == -1 and inputURL.find('https://') == -1:
            inputURL = 'http://' + inputURL
        return inputURL

    def _importTables(self, _):
        url = self.getInputURL()
        try:
            r = requests.get(url, allow_redirects=True)
            soup = BeautifulSoup(r.text, 'html.parser')
        except:
            self._showError(f'Error: Invalid URL.')
            return

        tables: [Table] = []

        table: element.Tag
        for table in soup.find_all('table'):
            tableRows = [[]]

            rows = table.find_all('tr')
            numRows = len(rows)
            for rowIdx in range(numRows):
                row: element.Tag = rows[rowIdx]
                for cell in row.find_all(['td', 'th']):
                    tableRows[-1].append(cell.text)
                if rowIdx != numRows - 1:
                    tableRows.append([])

            # use caption as title if it exists, else just the first cell text
            caption = table.find('caption')
            tableTitle = caption.get_text() if caption else tableRows[0][0]
            tableTitle = tableTitle.strip()
            tables.append(Table(tableRows, tableTitle))
        if len(tables) > 0:
            self._showTableSelector(tables)
        else:
            self._showError('No tables could be found on that page.')

    def _showTableSelector(self, tables):
        # Remove any existing buttons
        i = 0
        while self.getChild(f'btn{str(i)}') is not None:
            self.removeChild(f'btn{str(i)}')
            i += 1

        margin = 10
        buttonWidth = 300
        buttonHeight = 25
        yPos = 100  # starts below the 80px of UI at the top + a small margin
        for i in range(len(tables)):
            self.appendChild(Button(
                f'btn{str(i)}', (self.getWidth() - buttonWidth) // 2, yPos,
                height=buttonHeight, width=buttonWidth,
                text=tables[i].name or f'Table {i + 1}',
                # Lambdas evaluate variables at call-time, at which point i is
                # always the last value it took on. Use default parameter as
                # workaround--courtesy of https://stackoverflow.com/a/10452819
                action=lambda _, i=i: self._onTableConfirm(tables[i])))
            yPos += buttonHeight + margin

    def _onTableConfirm(self, table):
        result = self.props['onImport'](table)
        if result:
            self.dismiss()
        else:
            self._showError('Can\'t import—ensure columns do not overflow.')

    def _resetView(self):
        self.removeAllChildren()
        self.initChildren()

    def _showError(self, error):
        self.removeAllChildren()
        errorMargin = 40
        btnHeight = 15
        btnWidth = 50
        self.appendChild(Text('error-message',
                                  self.getWidth() // 2, errorMargin,
                                  text=error))
        self.appendChild(Button('error-retry',
                                (self.getWidth() - btnWidth) // 2,
                                self.getHeight() - errorMargin - btnHeight,
                                height=btnHeight,
                                width=btnWidth,
                                text='Retry',
                                action=lambda _: self._resetView()))
