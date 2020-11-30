# operators.py
# Joseph Rotella (jrotella, F0)
#
# Operator class and definitions.

# defines an abstract operator on arbitrarily many (numerical) operands
import math
import random


class Operator(object):
    _operators = {}

    def __init__(self, name, func, numerical=True):
        self.name = name
        self.func = func
        self.numerical = numerical
        Operator._operators[self.name] = self

    def _numberizeOperands(self, operands):
        newOperands = []
        for operand in operands:
            if isinstance(operand, int):
                newOperands.append(operand)
            else:
                try:
                    newOperands.append(int(operand.replace(',', '')))
                except:
                    newOperands.append(0)
        return newOperands

    def operate(self, operands):
        # TODO: make this more robust
        if self.numerical:
            operands = self._numberizeOperands(operands)
        return self.func(operands)

    @staticmethod
    def get(name):
        if name in Operator._operators:
            return Operator._operators[name]
        else:
            raise Exception(f'Illegal operator {name}')

# OPERATOR FUNCTIONS
def average(operands):
    return sum(operands) / len(operands)

def mode(operands):
    if operands == []:
        return 0
    occurrences = {}
    for el in operands:
        if el in occurrences:
            occurrences[el] += 1
        else:
            occurrences[el] = 1

    mostFrequentElements = []
    mostFrequentOccurrences = 0
    for el in occurrences:
        elOccurrences = occurrences[el]
        if elOccurrences > mostFrequentOccurrences:
            mostFrequentElements = [el]
            mostFrequentOccurrences = occurrences[el]
        elif elOccurrences == mostFrequentOccurrences:
            mostFrequentElements.append(el)
    return average(mostFrequentElements)

# OPERATOR DEFINITIONS

# Utility operator for literal formulae
Operator('LITERAL', lambda x: x[0], numerical=False)

Operator('ADD', sum)
Operator('AVERAGE', lambda x: sum(x) / len(x))
Operator('DIVIDE', lambda x: x[0] / math.prod(x[1:]))
Operator('MODE', mode)
Operator('MULTIPLY', math.prod)
Operator('RAND', lambda x: random.random())  # TODO: Figure out how to stop this recomputing when scrolling!
Operator('SUBTRACT', lambda x: x[0] - sum(x[1:]))
Operator('SUM', sum)
