from functools import reduce

from typing import Union

from data_structures import Stack
from operators import Operator

class Cell(object):
    def __init__(self):
        self.raw = ''
        self.formula = None

    _cells = {}

    @staticmethod
    def getValue(row, col):
        if (row, col) in Cell._cells:
            return Cell._cells[row, col].value()
        else:
            return ''

    @staticmethod
    def delete(row, col):
        if (row, col) in Cell._cells:
            del Cell._cells[row, col]

    # Sets raw value of cell as well as formula, if applicable
    # NOTE: will throw if formula illegal (i.e., syntax error)
    @staticmethod
    def setRaw(row, col, text):
        if (row, col) in Cell._cells:
            cell = Cell._cells[row, col]
        else:
            cell = Cell()
            Cell._cells[row, col] = cell
        cell.raw = text
        if cell.raw[0] == '=':
            cell.formula = Formula.fromText(cell.raw)

    # Returns computed value of cell (with appropriate type/formula result)
    def value(self):
        if self.formula:
            return self.formula.evaluate()
        else:
            try:
                return int(self.raw)
            except ValueError:
                return self.raw

    def __repr__(self):
        rep = f'Cell({self.raw}'
        if self.formula:
            rep += f' -> {self.formula}'
        rep += ')'
        return rep

# Represents a formula reference to a cell. We use refs instead of pointing
# to cells directly so that we don't end up with zombies (and unexpected
# behavior) if a previously-referenced cell is subsequently cleared/deleted
class CellRef(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def getValue(self):
        return Cell.getValue(self.row, self.col)

# represents a formula in a cell, where a formula is composed of an operator
# applied to multiple operands, each of which could be another formula,
# a cell reference, or a numerical literal
class Formula(object):
    def __init__(self, operator: Operator,
                 operands: list[Union[int, str, CellRef]]):
        self.operator = operator
        self.operands = operands

    @staticmethod
    def fromText(text):
        # remove leading equals sign, ditch spaces, ignore case
        text = text[1:].replace(' ', '').upper()
        return Formula._parseFormula(text)

    @staticmethod
    def _parseFormula(argString):
        activeFormulae = Stack()
        result = None
        for token, value in Formula._getTokens(argString):
            if token == '(':
                activeFormulae.push(Formula(Operator.get(value), []))
            elif token == ')':
                formula = activeFormulae.pop()
                formula.operands += Formula._getCellOrLiteral(value)
                containerFormula = activeFormulae.get()
                if containerFormula:
                    activeFormulae.get().operands.append(formula)
                else:
                    # We store the result rather than immediately returning
                    # it so that malformed expressions (i.e., where extra tokens
                    # follow what should be the end) are flagged as such
                    result = formula
            else:
                activeFormulae.get().operands += Formula._getCellOrLiteral(
                    value)
        return result

    # Iteratively returns all tokens and their preceding values in a given
    # formula string
    @staticmethod
    def _getTokens(formulaString):
        while True:
            nextOpen = formulaString.find('(')
            nextClose = formulaString.find(')')
            nextComma = formulaString.find(',')
            nonnegative = lambda x: x >= 0
            existentTokens = list(filter(nonnegative,
                                         [nextOpen, nextClose, nextComma]))
            if not existentTokens:
                return
            else:
                nextTokenIdx = min(existentTokens)
                nextToken = formulaString[nextTokenIdx]
                nextValue = formulaString[:nextTokenIdx]
                formulaString = formulaString[nextTokenIdx + 1:]
                yield nextToken, nextValue

    # Takes an input string and attempts to turn it into a cell reference;
    # if it isn't a valid cell reference, returns the literal value instead.
    # Returns as a list of 1 item. If the input is empty, returns empty list.
    @staticmethod
    def _getCellOrLiteral(text):
        if text == '':
            return []
        try:
            cellRow = int(text[1:]) - 1  # User-facing numbering is 1-based
            cellCol = ord(text[0]) - ord('A')
            return [CellRef(cellRow, cellCol)]
        except:
            # TODO: types
            return [int(text)]

    def evaluate(self):
        evaluatedOperands = []
        for operand in self.operands:
            if isinstance(operand, Formula):
                evaluatedOperands.append(operand.evaluate())
            elif isinstance(operand, CellRef):
                evaluatedOperands.append(operand.getValue())
            else:
                # TODO: for now, we just assume it's an appropriate data type
                evaluatedOperands.append(int(operand))
        return self.operator.operate(evaluatedOperands)

    def __repr__(self):
        operandsStr = reduce(lambda acc, val:
                             f'{acc}, {repr(val)}' if acc else val,
                             self.operands, '')
        return f'{self.operator.name}({operandsStr})'


# test cases
if __name__ == '__main__':
    assert (repr(
        Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, ADD(2, 3)), 2)'))
        == 'ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, ADD(2, 3)), 2)'
    )
    assert (repr(
        Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, ADD(3), 2)'))
        == 'ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, ADD(3), 2)'
    )
    assert (repr(
        Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, ADD(3))'))
        == 'ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, ADD(3))'
    )
    assert (repr(
        Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, 3)'))
        == 'ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, 3)'
    )
    assert (repr(
        Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9)'))
        == 'ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9)'
    )
