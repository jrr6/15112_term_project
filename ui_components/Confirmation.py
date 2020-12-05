# Confirmation.py
# Joseph Rotella (jrotella, F0)
#
# A generic modal view for confirming a user action.
from modular_graphics.atomic_elements import Text
from modular_graphics.input_elements import Button
from modular_graphics.modal import ModalView


class Confirmation(ModalView):
    def __init__(self, **props):
        super().__init__(props)
        self.height = 200
        self.width = 500
        self.buttonWidth = 100
        self.startY = 10
        self.yStep = 50

    def initChildren(self):
        if 'message' in self.props:
            text = self.props['message']
        else:
            text = ''

        if 'onConfirm' in self.props:
            onConfirm = self.props['onConfirm']
        else:
            onConfirm = lambda: None

        y = self.startY
        self.appendChild(Text(
            'label', self.width // 2, self.startY, text=text
        ))
        y += self.yStep
        self.appendChild(Button(
            'submit', (self.width - self.buttonWidth) // 2, y, text='Cancel',
            width=self.buttonWidth))
        self.appendChild(Button(
            'submit', (self.width + self.buttonWidth) // 2, y, text='OK',
            width=self.buttonWidth, action=onConfirm))

    def onSubmit(self, _):
        input = self.getChild('path').text
        self.props['onSubmit'](input)
        self.dismiss()

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
