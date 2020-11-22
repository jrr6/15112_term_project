import string

from cmu_112_graphics import App as CMUApp, WrappedCanvas
from abc import ABC, abstractmethod

class RelativeCanvas(object):
    def __init__(self, canvas: WrappedCanvas, x, y):
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
        self.id = name
        self.props = props
        self.x = x
        self.y = y
        self.children = []
        self.childIds = {}

    def draw(self, canvas: RelativeCanvas):
        for child in self.children:
            child.draw(RelativeCanvas(canvas.canvas, child.x, child.y))

    @abstractmethod
    def getWidth(self):
        pass

    @abstractmethod
    def getHeight(self):
        pass

    def appendChild(self, element):
        element.x += self.x
        element.y += self.y
        self.children.append(element)
        self.childIds[element.id] = element

    def hasChild(self, name):
        return name in self.childIds

    def getChild(self, name):
        if self.hasChild(name):
            return self.childIds[name]

    def removeChild(self, name):
        if self.hasChild(name):
            self.children.remove(self.childIds[name])
            del self.childIds[name]

    def onClick(self, x, y):
        pass

    def onKeypress(self, event):
        pass

    def makeKeyListener(self):
        listeners = App.instance.keyListeners
        if self not in listeners:
            listeners.append(self)

    def resignKeyListener(self):
        listeners = App.instance.keyListeners
        if self in listeners:
            listeners.remove(self)

class TextField(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.active = False
        self.height = 25
        self.width = 100
        self.text = ''

        self.appendChild(Rectangle('border', 0, 0, width=self.width,
                                   height=self.height))
        self.appendChild(Text('placeholder', 10, 5, text='Enter text',
                              fill='gray', anchor='nw'))
        self.appendChild(Text('input', 10, 5, text=self.text, anchor='nw'))

    def onClick(self, x, y):
        if not self.active:
            self.removeChild('placeholder')
            self.getChild('border').props['fill'] = 'gray'
            self.makeKeyListener()

    def onKeypress(self, event):
        print(event.key)
        if event.key == 'Enter':
            self.active = False
            self.getChild('border').props['fill'] = None
            self.resignKeyListener()
            return

        if event.key == 'Space':
            self.text += ' '
        elif event.key == 'Delete':
            self.text = self.text[:-1]
        elif event.key in string.ascii_letters + string.punctuation:
            self.text += event.key

        charsToShow = 12
        self.getChild('input').props['text'] = self.text[-charsToShow:]

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class Button(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = props.get('width', 200)
        self.height = props.get('height', 100)

        self.appendChild(Rectangle('border', 0, 0,
                                   width=self.width, height=self.height))
        if 'text' in self.props:
            self.appendChild(Text('label', self.width // 2, self.height // 2,
                                  text=self.props['text']))

    def onClick(self, x, y):
        if 'action' in self.props:
            self.props['action'](self)

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width


class Rectangle(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = props.get('width', 0)
        self.height = props.get('height', 0)

    def draw(self, canvas):
        fill = self.props.get('fill', None)
        canvas.createRectangle(0, 0, self.width, self.height, fill=fill)

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


class Text(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)

    def draw(self, canvas):
        canvas.createText(0, 0, text=self.props.get('text', ''),
                          font=self.props.get('font', 'Courier 12'),
                          anchor=self.props.get('anchor', 'center'))

    def getHeight(self):
        return 0

    def getWidth(self):
        return 0

class Scene(UIElement):
    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = props.get('width', 0)
        self.height = props.get('height', 0)

        self.appendChild(Button('button1', 100, 50, text='hello',
                                action=self.toggleButton2))
        self.appendChild(Button('button2', 300, 50,
                                action=lambda button:
                                print('You pressed the button!')))
        self.appendChild(Text('text1', 200, 30, text='Hello, World!'))
        self.appendChild(TextField('textField', 100, 300))

    def toggleButton2(self, sender):
        if self.hasChild('button2'):
            self.removeChild('button2')
        else:
            self.appendChild(Button('button2', 300, 50,
                                    action=lambda button:
                                    print('You pressed the button!')))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

class App(CMUApp, UIElement):
    instance = None

    def __init__(self, width, height):
        UIElement.__init__(self, 'root', 0, 0, {})
        self.width = width
        self.height = height
        # IMPORTANT: set autorun to false or init will never finish!
        CMUApp.__init__(self, width=self.width, height=self.height,
                        autorun=False)
        self.keyListeners = []
        self.appendChild(Scene('scene', 0, 0,
                               width=self.width, height=self.height))

    @staticmethod
    def start():
        # TODO: Put app dimensions somewhere more obvious
        App.instance = App(600, 600)
        App.instance.run()

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

    def keyPressed(self, event):
        for listener in self.keyListeners:
            listener.onKeypress(event)

    def redrawAll(self, canvas):
        self.draw(RelativeCanvas(canvas, 0, 0))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

App.start()
