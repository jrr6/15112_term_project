# data_structures.py
# Joseph Rotella (jrotella, F0)
#
# Contains implementations of useful data structures.

class Stack(object):
    class Item(object):
        def __init__(self, value, pointer):
            self.value = value
            self.pointer = pointer

    def __init__(self):
        self.top = None

    def get(self):
        if not self.top:
            return None
        return self.top.value

    def push(self, item):
        if self.top:
            pointer = self.top
        else:
            pointer = None
        newItem = Stack.Item(item, pointer)
        self.top = newItem

    def pop(self):
        if self.top:
            result = self.top.value
            self.top = self.top.pointer
            return result
        else:
            return None
