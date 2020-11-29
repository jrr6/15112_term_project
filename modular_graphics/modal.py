from modular_graphics.atomic_elements import Rectangle, Text
from modular_graphics.input_elements import Button
from modular_graphics import UIElement

# A class that views that intend to be displayed as modal subviews can subclass
# to ensure they don't do anything weird with name/coords (since Modal will
# hijack/not care about all of that anyway)
class ModalView(UIElement):
    def __init__(self, props):
        super().__init__('modalview', 0, Modal.kViewTopMargin, props)

# Displays an arbitrary subview in modal format
class Modal(UIElement):
    kCloseButtonSize = 15
    kCloseButtonMargin = 10
    kViewTopMargin = kCloseButtonSize + kCloseButtonMargin

    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.message = props.get('message', '')
        self.input = props.get('input', False)
        # you can't create a modal without a subview!
        self.subview = props['view']

    def initChildren(self):
        self.appendChild(Rectangle('modal-container', 0, 0,
                                   width=self.getWidth(),
                                   height=self.getHeight(),
                                   outline='black', fill='white'))
        # Modals have to be dismissable or they totally ruin everything,
        # so I think it's okay to crash if we don't have that prop
        # Also, we throw away the sender b/c the dismisser doesn't care
        self.appendChild(Button('close', Modal.kCloseButtonMargin,
                                Modal.kCloseButtonMargin,
                                height=Modal.kCloseButtonSize,
                                width=Modal.kCloseButtonSize, text='X',
                                action=lambda _: self.props['onDismiss']()))
        self.appendChild(self.subview)

    def getHeight(self):
        return self.subview.getHeight() + Modal.kViewTopMargin

    def getWidth(self):
        return self.subview.getWidth()
