# modular_graphics.py
# Joseph Rotella (jrotella, F0)
#
# A framework atop 112 graphics that allows for modular UI elements with
# independent states and event-driven design patterns.
import copy

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
        self.name = name
        self.props = props
        self.x = x
        self.y = y
        self.children = []
        self.childIds = {}

    def draw(self, canvas: RelativeCanvas):
        for child in self.children:
            child.draw(RelativeCanvas(canvas.canvas, child.x, child.y))

    def initChildren(self):
        pass

    @abstractmethod
    def getWidth(self):
        pass

    @abstractmethod
    def getHeight(self):
        pass

    def appendChild(self, element):
        element.x += self.x
        element.y += self.y
        # We must init children AFTER changing the x,y
        # or the child won't get those changes
        element.initChildren()
        self.children.append(element)
        self.childIds[element.name] = element

    def hasChild(self, name):
        return name in self.childIds

    def getChild(self, name):
        if self.hasChild(name):
            return self.childIds[name]

    def removeChild(self, name):
        if self.hasChild(name):
            self.children.remove(self.childIds[name])
            del self.childIds[name]

    def removeAllChildren(self):
        self.children = []

    def onClick(self, event):
        pass

    def onKeypress(self, event):
        pass

    def makeKeyListener(self):
        listeners = App.keyListeners
        if self not in listeners:
            listeners.append(self)

    def resignKeyListener(self):
        listeners = App.keyListeners
        if self in listeners:
            listeners.remove(self)

class App(CMUApp, UIElement):
    instance = None

    # TODO: Making this class-level feels wrong, but we need it to be accessible
    #       before App is finished initing (otherwise we can't register key
    #       listeners in `initChildren()`)
    keyListeners = []

    def __init__(self, scene):
        UIElement.__init__(self, 'root', 0, 0, {})
        self.width = scene.getWidth()
        self.height = scene.getHeight()
        # IMPORTANT: set autorun to false or init will never finish!
        CMUApp.__init__(self, width=self.width, height=self.height,
                        autorun=False)
        self.appendChild(scene)

    @staticmethod
    def load(scene):
        App.instance = App(scene)
        App.instance.run()

    def mousePressed(self, event):
        App._addEventMetadata(event)
        childIdx = len(self.children) - 1
        while childIdx >= 0:
            curChild = self.children[childIdx]
            self.processMouseEvent(curChild, event)
            childIdx -= 1

    def processMouseEvent(self, element: UIElement, event):
        propagateToChildren = True
        if (element.x <= event.x <= element.x + element.getWidth()
                and element.y <= event.y <= element.y + element.getHeight()):
            # This would be easier with copy.(deep)copy, but we get pickling
            # errors
            oldX = event.x
            oldY = event.y
            event.x -= element.x
            event.y -= element.y

            def stopPropagation():
                nonlocal propagateToChildren
                propagateToChildren = False

            event.stopPropagation = stopPropagation
            element.onClick(event)
            event.x = oldX
            event.y = oldY

        if propagateToChildren:
            for child in element.children:
                self.processMouseEvent(child, event)

    def keyPressed(self, event):
        App._addEventMetadata(event)
        # Elements might resign key listener status when this is triggered,
        # so make a copy so we don't skip anyone
        for listener in copy.copy(App.keyListeners):
            listener.onKeypress(event)

    def redrawAll(self, canvas):
        self.draw(RelativeCanvas(canvas, 0, 0))

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    @staticmethod
    def _addEventMetadata(event):
        # Add checks for modifier keys
        event.shiftDown = (event.state & 0x1 != 0)
        event.controlDown = (event.state & 0x4 != 0)
        event.commandDown = (event.state & 0x8 != 0)
        event.optionDown = (event.state & 0x10 != 0)
