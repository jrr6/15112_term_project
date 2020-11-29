# WebImporter.py
# Joseph Rotella (jrotella, F0)
#
# Contains the UI for the web scraper/importer to be displayed as a modal.
import requests
from bs4 import BeautifulSoup, element

from modular_graphics.atomic_elements import Text
from modular_graphics.input_elements import Button
from modular_graphics.modal import ModalView

class Table(object):
    def __init__(self, rows, name):
        self.rows = rows
        self.name = name

class WebImporter(ModalView):
    def __init__(self, **props):
        super().__init__(props)
        self.width = 300
        self.height = 100
        if 'onImport' not in props:
            raise Exception('Attempt to construct WebImporter without handler.')

    def initChildren(self):
        self.appendChild(Button('demo', 10, 10, text='PLACEHOLDER',
                                width=100, height=20,
                         action=lambda _: self._importTables('notasite')))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def _importTables(self, url):
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
            tables.append(Table(tableRows, tableTitle))
        if len(tables) > 0:
            self._showTableSelector(tables)
        else:
            self._showError('No tables could be found on that page.')

    def _showTableSelector(self, tables):
        pass

    def _resetView(self):
        self.removeAllChildren()
        self.initChildren()

    def _showError(self, error):
        self.removeAllChildren()
        errorMargin = 10
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
