# formulae
# Joseph Rotella (jrotella, F0)
#
# Contains main classes for formula parsing, representation, and evaluation.
import string
from functools import reduce

from typing import Union

from formulae.data_structures import Stack, DependencyGraph
from formulae.operators import Operator
from utils import splitEscapedString


class Cell(object):
    def __init__(self):
        self.raw = ''
        self.formula = None

    _cells = {}
    _deps = DependencyGraph()

    @staticmethod
    def getValue(row, col):
        if (row, col) in Cell._cells:
            return Cell._cells[row, col].value()
        else:
            return ''

    @staticmethod
    def getRaw(row, col):
        if (row, col) in Cell._cells:
            return Cell._cells[row, col].raw
        else:
            return ''

    @staticmethod
    def hasFormula(row, col):
        if (row, col) in Cell._cells:
            return Cell._cells[row, col].formula is not None

    @staticmethod
    def delete(row, col):
        if (row, col) in Cell._cells:
            Cell._deps.setDependencies(CellRef(row, col), set())
            del Cell._cells[row, col]

    # Sets raw value of cell as well as formula, if applicable
    # By default, will throw if formula illegal. If you REALLY, REALLY promise
    # to handle the error elsewhere
    @staticmethod
    def setRaw(row, col, text):
        if (row, col) in Cell._cells:
            cell = Cell._cells[row, col]
        else:
            cell = Cell()
            Cell._cells[row, col] = cell
        cell.raw = text
        if len(cell.raw) > 0 and cell.raw[0] == '=':
            cell.formula = Formula.fromText(cell.raw)
            print('cell.formula =', cell.formula, 'with deps', cell.formula.getDependencies())
            Cell._deps.setDependencies(CellRef(row, col),
                                       cell.formula.getDependencies())
        else:
            cell.formula = None
            Cell._deps.setDependencies(CellRef(row, col), set())

    @staticmethod
    def getDependents(row, col):
        return Cell._deps.getDependents(CellRef(row, col))

    @staticmethod
    def getShallowDependencies(row, col):
        return Cell._deps.getShallowDependencies(CellRef(row, col))

    @staticmethod
    def empty():
        return len(Cell._cells) == 0

    # serializes a raw cell content dictionary, obtainable from
    # Cell.getRawCells()
    @staticmethod
    def serializeRaw(rawCells):
        result = ''
        for cellLoc in rawCells:
            cellRaw = rawCells[cellLoc]
            escaped = cellRaw.replace(',', '\\,')
            result += f'{cellLoc[0]},{cellLoc[1]},{escaped},'
        result = result[:-1]  # strip trailing comma
        return result

    # returns all current cells as a string dictionary suitable for loading
    # via loadRawCells()
    @staticmethod
    def getRawCells():
        rawDict = {}
        for row, col in Cell._cells:
            rawDict[row, col] = Cell._cells[row, col].raw
        return rawDict

    # replaces stored cell data with data from provided cells,
    # or simply resets all cells if None is passed
    @staticmethod
    def loadRawCells(cells: Union[None, dict[tuple[int, int], str]]):
        Cell._cells = {}
        Cell._deps = DependencyGraph()
        if cells is not None:
            for row, col in cells:
                try:
                    Cell.setRaw(row, col, cells[row, col])
                except:
                    # if there's a syntax error, the spreadsheet grid will
                    # figure it out when it loads
                    pass

    # deserializes serialized cells and returns a string dictionary suitable
    # for loading via loadRawCells()
    @staticmethod
    def deserializeRawCells(data: Union[str, None]):
        res = {}
        if data is None or data == '':
            return
        curRow, curCol = None, None
        entities = splitEscapedString(data, ',')
        for i in range(len(entities)):
            if i % 3 == 0:
                curRow = int(entities[i])
            elif i % 3 == 1:
                curCol = int(entities[i])
            else:
                deEscaped = entities[i].replace('\\,', ',')
                res[curRow, curCol] = deEscaped
            i += 1
        return res

    # Returns computed value of cell (with appropriate type/formula result)
    def value(self):
        if self.formula:
            try:
                return self.formula.evaluate()
            except:
                return 'RUNTIME-ERROR'
        else:
            try:
                return int(self.raw)
            except:
                try:
                    return float(self.raw)
                except:
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

    def serialize(self):
        return f'{self.row}:{self.col}'

    @staticmethod
    def deserialize(data):
        entities = data.split(':')
        return CellRef(int(entities[0]), int(entities[1]))

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return (isinstance(other, CellRef)
                and other.row == self.row and other.col == self.col)

    def __repr__(self):
        return f'CellRef({self.row}, {self.col})'

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

        foundTokens = False
        for token, value in Formula._getTokens(argString):
            foundTokens = True
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

        if not foundTokens:  # Something like `=D4` or `=2`
            operand = Formula._getCellOrLiteral(argString)
            if len(operand) > 1:
                raise Exception('Formula literal cannot be multiple values')
            result = Formula(Operator.get('LITERAL'), operand)

        # TODO: Figure out why the types of the operands aren't consistent
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

        if ':' in text:
            cells = text.split(':')
            if len(cells) != 2:
                print('i')
                raise Exception('Illegal cell range format')
            cell0 = Formula._getCellOrLiteral(cells[0])[0]
            cell1 = Formula._getCellOrLiteral(cells[1])[0]
            if not isinstance(cell0, CellRef) or not isinstance(cell1, CellRef):
                raise Exception('Illegal entity in cell range')
            startCol = min(cell0.col, cell1.col)
            endCol = max(cell0.col, cell1.col)
            startRow = min(cell0.row, cell1.row)
            endRow = max(cell0.row, cell1.row)

            cellsInRange = []
            for row in range(startRow, endRow + 1):
                for col in range(startCol, endCol + 1):
                    cellsInRange.append(CellRef(row, col))
            return cellsInRange

        hasRowNum = True
        for char in text[1:]:
            if char not in string.digits:
                hasRowNum = False
                break

        if text[0] in string.ascii_uppercase and hasRowNum:
            cellRow = int(text[1:]) - 1  # User-facing numbering is 1-based
            cellCol = ord(text[0]) - ord('A')
            return [CellRef(cellRow, cellCol)]
        else:
            return [text]

    def evaluate(self):
        evaluatedOperands = []
        for operand in self.operands:
            if isinstance(operand, Formula):
                evaluatedOperands.append(operand.evaluate())
            elif isinstance(operand, CellRef):
                evaluatedOperands.append(operand.getValue())
            else:
                evaluatedOperands.append(operand)
        return self.operator.operate(evaluatedOperands)

    def getDependencies(self):
        deps = set()
        for operand in self.operands:
            if isinstance(operand, CellRef):
                deps.add(operand)
            elif isinstance(operand, Formula):
                deps = deps.union(operand.getDependencies())
        return deps

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
