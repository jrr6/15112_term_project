# SheetConfiguration.py
# Joseph Rotella (jrotella, F0)
#
# Contains the sheet configuration UI view.

from modular_graphics.atomic_elements import Text
from modular_graphics.input_elements import TextField, Button
from modular_graphics.modal import ModalView

class SheetConfiguration(ModalView):
    def __init__(self, **props):
        super().__init__(props)
        self.width = 400
        self.height = 180
        self.buttonWidth = 100
        self.margin = 10
        self.labelWidth = 80
        self.textFudgeY = 12
        self.headerY = self.margin
        self.fieldY = 30
        self.fieldWidth = 200
        self.fieldChars = 25
        self.deleteY = 80
        self.submitY = 120
        if 'onSave' not in self.props or 'onDelete' not in self.props\
                or 'name' not in self.props or 'index' not in self.props:
            raise Exception('Missing required props for sheet configurator')

    def initChildren(self):
        self.appendChild(Text('header', self.width // 2, self.headerY,
                              text='Sheet Configuration',
                              font='"Andale Mono" 14', anchor='center'))

        self.appendChild(Text('label', self.margin,
                              self.fieldY + self.textFudgeY,
                              text='Sheet Title', anchor='w'))
        self.appendChild(TextField('input', self.margin * 2 + self.labelWidth,
                                   self.fieldY, width=self.fieldWidth,
                                   visibleChars=self.fieldChars,
                                   text=self.props['name'],
                                   placeholder=None))

        self.appendChild(Button('delete-button',
                                (self.width - self.buttonWidth) // 2,
                                self.deleteY, width=self.buttonWidth,
                                text='Delete Sheet',
                                action=self.onDelete))

        self.appendChild(Button('save-button',
                                (self.width - self.buttonWidth) // 2,
                                self.submitY, width=self.buttonWidth,
                                text='Save Changes',
                                action=self.onSave))

    def onSave(self, _):
        self.props['onSave'](self.props['index'], self.getChild('input').text)
        self.dismiss()

    def onDelete(self, _):
        self.props['onDelete'](self.props['index'])
        self.dismiss()

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
