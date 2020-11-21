from cmu_112_graphics import App
from abc import ABC, abstractmethod

def drawfunc(f):
    def wrapped(self, canvas):
        f(self, RelativeCanvas(canvas, self.x, self.y))
    return wrapped

class RelativeCanvas(object):
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y

    def createRectangle(self, x0, y0, x1, y1, **kwargs):
        self.canvas.create_rectangle(x0 + self.x, y0 + self.y,
                                     x1 + self.x, y1 + self.y, **kwargs)

    def createText(self, x, y, **kwargs):
        self.canvas.create_text(x + self.x, y + self.y, **kwargs)

class UIElement(ABC):
    def __init__(self, name, x, y, props):
        # print('UIElement init', type(self))
        self.id = name
        self.props = props
        self.x = x
        self.y = y
        self.children = []
        self.childIds = {}

    @abstractmethod
    def draw(self, canvas):
        pass

    @abstractmethod
    def getWidth(self):
        pass

    @abstractmethod
    def getHeight(self):
        pass

    def drawChildren(self):
        for child in self.children:
            child.draw()

    def appendChild(self, element):
        self.children.append(element)
        self.childIds[element.id] = element

    def removeNamedChild(self, name):
        if name in self.childIds:
            self.children.remove(self.childIds[name])
            del self.childIds[name]

    def onClick(self, x, y):
        pass

class Button(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = 200
        self.height = 100

    @drawfunc
    def draw(self, canvas):
        canvas.createRectangle(0, 0, self.getWidth(), self.getHeight(),
                               fill=self.props.get('color', 'white'))
        if 'text' in self.props:
            canvas.createText(self.width // 2, self.height // 2,
                              text=self.props['text'])

    def onClick(self, x, y):
        if 'action' in self.props:
            self.props['action'](self)

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class Text(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.text = props.get('text', '')
        self.font = props.get('font', 'SFUI 12')

    @drawfunc
    def draw(self, canvas):
        canvas.createText(0, 0, text=self.text, font=self.font)

    def getHeight(self):
        return 0

    def getWidth(self):
        return 0

class SpreadsheetApp(App, UIElement):
    def __init__(self, width, height):
        # TODO: there's got to be a more elegant solution
        UIElement.__init__(self, 'root', 0, 0, [])
        App.__init__(self, width=width, height=height)

    def toggleButton2(self, sender):
        if 'button2' in self.childIds:
            self.removeNamedChild('button2')
        else:
            self.appendChild(Button('button2', 300, 50,
                                        action=lambda button:
                                        print('You pressed the button!')))

    def appStarted(self):
        self.appendChild(Button('button1', 100, 50, text='hello',
                         action=self.toggleButton2))
        self.appendChild(Button('button2', 300, 50,
                                action=lambda button:
                                print('You pressed the button!')))
        self.appendChild(Text('text1', 200, 30, text='Hello, World!'))

    def mousePressed(self, event):
        childIdx = len(self.children) - 1
        while childIdx >= 0:
            curChild = self.children[childIdx]
            self.processMouseEvent(curChild, event.x, event.y,
                                   curChild.x, curChild.y)
            childIdx -= 1

    def processMouseEvent(self, element: UIElement, eventX, eventY,
                          offsetX, offsetY):
        if (offsetX <= eventX <= offsetX + element.getWidth()
                and offsetY <= eventY <= offsetY + element.getHeight()):
            element.onClick(eventX - offsetX, eventY - offsetY)
        for child in element.children:
            self.processMouseEvent(child, eventX, eventY,
                                   offsetX + child.x, offsetY + child.y)

    # TODO: Make this recursive as well
    # Also, we may not need @drawfunc -- just wrap the canvas here
    # IN FACT, if we make all things classes instead of canvas.* methods,
    # we can avoid MVC violations and still build up the UI (just do it
    # IN CONTROLLER)
    def redrawAll(self, canvas):
        self.draw(canvas)
        for child in self.children[::-1]:  # draw last-added child first
            child.draw(canvas)

    def draw(self, canvas):
        pass

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

SpreadsheetApp(width=600, height=600)

'''

class CellGrid(UIElement):
    def __init__(self, props):
        super().__init__(props)

    def draw(self, canvas, x, y):
        pass

class MenuBar(UIElement):
    pass

'''