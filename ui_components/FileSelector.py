# FileSelector.py
# Joseph Rotella (jrotella, F0)
#
# Contains the modal view for opening and saving files.
from modular_graphics.atomic_elements import Text
from modular_graphics.input_elements import TextField, Button
from modular_graphics.modal import ModalView


class FileSelector(ModalView):
    def __init__(self, **props):
        super().__init__(props)
        self.height = 200
        self.width = 500
        self.fieldWidth = 400
        self.fieldChars = 54
        self.buttonWidth = 30
        self.startY = 10
        self.yStep = 50
        if 'onSubmit' not in self.props:
            raise Exception('Attempt to run file modal without submit action')

    def initChildren(self):
        y = self.startY
        if 'message' in self.props:
            text = self.props['message']
        else:
            text = 'File Selector'
        self.appendChild(Text(
            'label', self.width // 2, self.startY, text=text
        ))
        y += self.yStep
        self.appendChild(TextField(
            'path', (self.width - self.fieldWidth) // 2, y,
            placeholder='Enter a path', width=self.fieldWidth,
            visibleChars=self.fieldChars))
        y += self.yStep
        self.appendChild(Button(
            'submit', (self.width - self.buttonWidth) // 2, y, text='OK',
            width=self.buttonWidth, action=self.onSubmit))

    def onSubmit(self, _):
        input = self.getChild('path').text
        self.props['onSubmit'](input)
        self.dismiss()

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
