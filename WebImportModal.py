from modular_graphics.atomic_elements import Rectangle, Text
from modular_graphics.input_elements import TextField, Button
from modular_graphics import UIElement

class Modal(UIElement):
    kWidth = 500
    kInputHeight = 300
    kNoInputHeight = 100

    def __init__(self, name, x, y, **props):
        super().__init__(name, x, y, props)
        self.width = Modal.kWidth
        self.message = props.get('message', '')
        self.input = props.get('input', False)
        if self.input:
            self.height = Modal.kInputHeight
        else:
            self.height = Modal.kNoInputHeight

    def initChildren(self):
        textX, textY = self.width // 2, 30
        inputWidth = 200
        inputX, inputY = self.width // 2 - inputWidth // 2, 150
        buttonWidth = 75
        buttonX, buttonY = self.width // 2 - buttonWidth // 2, self.height - 50
        self.appendChild(Rectangle('modal-container', 0, 0,
                                   width=self.width, height=self.height,
                                   outline='black', fill='white'))
        self.appendChild(Text('modal-text', textX, textY, text=self.message,
                              anchor='center'))
        if self.input:
            self.appendChild(TextField('modal-input-field', inputX, inputY,
                                       width=inputWidth))
        self.appendChild(Button('modal-confirm', buttonX, buttonY,
                                width=buttonWidth, text='OK',
                                action=self.submit))
        # TODO: The caller needs to block out events going to objects "shadowed"
        #       by the modal--right now we're having issues b/c the cells
        #       behind the modal are inadvertently triggering on click/key

    def submit(self, sender):
        print('submitted')
        if self.input:
            inputValue = self.getChild("modal-input-field").text
        else:
            inputValue = None

        if 'onSubmit' in self.props:
            self.props['onSubmit'](self, inputValue)

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width
