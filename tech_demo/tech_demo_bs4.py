from bs4 import BeautifulSoup, element
import requests
from cmu_112_graphics import *

class Table(object):
    def __init__(self, rows, name):
        self.rows = rows
        self.name = name

    def getColDisplayWidths(self):
        cellWidths = []
        for row in self.rows:
            for colIdx in range(len(row)):
                cellText = row[colIdx][0]
                if len(cellWidths) <= colIdx:
                    cellWidths.append(len(cellText) + 5)
                elif cellWidths[colIdx] < len(cellText):
                    cellWidths[colIdx] = len(cellText) + 5
        return cellWidths

    def __str__(self):
        res = ''
        cellWidths = self.getColDisplayWidths()

        for row in self.rows:
            for cellIdx in range(len(row)):
                cell = row[cellIdx]
                if cell[1]:
                    res += cell[0].upper().ljust(cellWidths[cellIdx])
                else:
                    res += cell[0].ljust(cellWidths[cellIdx])
            res += '\n'
        return res

def appStarted(app):
    # TODO: Learn more about requests
    # r = requests.get('https://datatables.net/manual/styling/classes', allow_redirects=True)
    r = requests.get('https://www.cmu.edu/coronavirus/health-and-wellness/dashboard.html', allow_redirects=True)
    soup = BeautifulSoup(r.text, 'html.parser')

    tables: [Table] = []

    table: element.Tag
    for table in soup.find_all('table'):
        tableRows = [[]]

        rows = table.find_all('tr')
        numRows = len(rows)
        for rowIdx in range(numRows):
            row: element.Tag = rows[rowIdx]
            for cell in row.find_all(['td', 'th']):
                isHeader = rowIdx == 0 or cell.name == 'th'
                tableRows[-1].append((cell.text, isHeader))
            if rowIdx != numRows - 1:
                tableRows.append([])

        caption = table.find('caption')
        tableTitle = caption.text if caption else tableRows[0][0][0]
        tables.append(Table(tableRows, tableTitle))

    for table in tables:
        print(f'--------------{table.name.strip()}--------------')
        print(table)

    app.tables = tables

def redrawAll(app, canvas):
    startX = 15
    startY = 15
    padding = 3
    cellHeight = 20
    curX = startX
    curY = startY

    for table in app.tables:
        colWidths = list(map(lambda x: 7*x, table.getColDisplayWidths()))
        canvas.create_text(curX + sum(colWidths) / 2,
                           curY + padding,
                           text=table.name, font='Courier 14 bold')
        curY += cellHeight
        for row in table.rows:
            for colIdx in range(len(row)):
                cell = row[colIdx]
                if cell[1]:
                    thickness = 3
                    textX = curX + colWidths[colIdx] / 2
                    textAnchor = 'n'
                    fontWeight = 'bold'
                else:
                    thickness = 1
                    textX = curX + padding
                    textAnchor = 'nw'
                    fontWeight = ''

                canvas.create_rectangle(curX, curY, curX + colWidths[colIdx],
                                        curY + cellHeight, width=thickness)
                canvas.create_text(textX, curY + padding,
                                   text=cell[0], anchor=textAnchor,
                                   font=f'Courier 12 {fontWeight}')
                curX += colWidths[colIdx]
            curY += cellHeight
            curX = startX
        curY += 3 * cellHeight

runApp(width=600, height=600)