# operators.py
# Joseph Rotella (jrotella, F0)
#
# Operator class and definitions.

import math
import random


# defines an abstract operator on arbitrarily many (numerical) operands
class Operator(object):
    _operators = {}

    def __init__(self, name, func, numerical=True, operandLimit=None):
        self.name = name
        self.func = func
        self.numerical = numerical
        self.operandLimit = operandLimit
        Operator._operators[self.name] = self

    def _numberizeOperands(self, operands):
        newOperands = []
        for operand in operands:
            if isinstance(operand, int) or isinstance(operand, float):
                newOperands.append(operand)
            else:
                try:
                    newOperands.append(int(operand.replace(',', '')))
                except:
                    try:
                        newOperands.append(float(operand.replace(',', '')))
                    except:
                        # TODO: should we "zeroify" or just skip?
                        # newOperands.append(0)
                        pass
        return newOperands

    def operate(self, operands):
        # TODO: make this more robust
        if self.operandLimit and len(operands) > self.operandLimit:
            raise Exception('Too many operands')
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
    if operands == []: return 0
    return sum(operands) / len(operands)

def safe(fn):
    def safeFn(operands):
        return fn(operands) if operands != [] else 0
    return safeFn

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
Operator('LITERAL', lambda x: x[0], numerical=False, operandLimit=1)

Operator('COUNT', lambda x: len(x), numerical=False)

Operator('ABS', lambda x: abs(x[0]), operandLimit=1)
Operator('ADD', sum)
Operator('AVERAGE', average)
Operator('DIVIDE', lambda x: x[0] / math.prod(x[1:]), operandLimit=2)
Operator('MIN', safe(min))
Operator('MAX', safe(max))
Operator('MODE', mode)
Operator('MULTIPLY', math.prod)
Operator('RAND', lambda x: random.random())  # TODO: Figure out how to stop this recomputing when scrolling!
Operator('SUBTRACT', lambda x: x[0] - sum(x[1:]), operandLimit=2)
Operator('SUM', sum)
