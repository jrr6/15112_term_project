import math

from cmu_112_graphics import *

def appStarted(app):
    # state parameters
    app.activePath = None

    # ui constants
    app.cellWidth = 100
    app.cellHeight = 60
    app.gridX0 = 5
    app.gridY0 = 20
    sizeChanged(app)

def sizeChanged(app):
    app.gridX1 = app.width  # - app.gridX0
    app.gridY1 = app.height  # - app.gridY0
    app.rows = int(math.ceil((app.gridY1 - app.gridY0) / app.cellHeight))
    app.cols = int(math.ceil((app.gridX1 - app.gridX0) / app.cellWidth))

def getCellBounds(app, row, col):
    x0 = app.gridX0 + col * app.cellWidth
    y0 = app.gridY0 + row * app.cellHeight
    x1 = x0 + app.cellWidth
    y1 = y0 + app.cellHeight
    return x0, y0, x1, y1

def drawSpreadsheetGrid(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            canvas.create_rectangle(*getCellBounds(app, row, col))

def redrawAll(app, canvas):
    drawSpreadsheetGrid(app, canvas)

def main():
    runApp(width=600, height=400)

if __name__ == '__main__':
    main()
