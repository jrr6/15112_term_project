import string
from functools import reduce

from typing import Union
from operators import Operator

# TODO: we need to be able to represent cells in our formulae
class Cell(object):
    @staticmethod
    def get(coords):
        return Cell()

    def value(self):
        pass

# represents a formula in a cell, where a formula is composed of an operator
# applied to multiple operands, each of which could be another formula,
# a cell reference, or a numerical literal
class Formula(object):
    def __init__(self, operator: Operator,
                 operands: list[Union[int, str, Cell]]):
        self.operator = operator
        self.operands = operands

    @staticmethod
    def fromText(text):
        # remove leading equals sign, ditch spaces, ignore case
        text = text[1:].replace(' ', '').upper()
        return Formula._parseFormula(text)

    @staticmethod
    def _parseFormula(text):
        callSite = text.find('(')
        if callSite == -1:
            operand = Formula._getCellOrLiteral(text)
            return Formula(Operator.get('LITERAL'), [operand])
        else:
            operator = text[:callSite]
            argString = text[callSite + 1:-1]
            arguments, _ = Formula._parseArgs(argString)
            return Formula(Operator.get(operator), arguments)

    # parses the arguments for the first call found, returning the arguments
    # as well as any remainder following the args to the first call (mostly
    # for recursive purposes)
    @staticmethod
    def _parseArgs(argString):
        # edge case: split() will return an annoying empty string if we let
        #            this fall through
        if argString == '':
            return [], ''
        nextCallLoc = argString.find('(')
        nextEndLoc = argString.find(')')
        if nextCallLoc == -1 and nextEndLoc == -1:
            rawArgs = argString.split(',')
            # args = list(map(Formula._getCellOrLiteral, rawArgs))
            args = rawArgs
            return args, ''
        elif nextCallLoc != -1 and nextCallLoc < nextEndLoc:
            # We find the next formula call, extract all literal/cell args
            # prior thereto, construct a formula for the call,
            # and extract all literal/cell args following the formula

            # find all comma-separated entities preceding the call
            priorEntities = argString[:nextCallLoc].split(',')
            # the last entity is the name of the operator itself
            operatorName = priorEntities.pop()
            # if there are no prior arguments, we'll have an annoying empty-str
            # priorArgs = [] if priorEntities == [''] else priorEntities

            # these are only literals, but this avoids having to reimplement
            # code
            priorArgs, _ = Formula._parseArgs(','.join(priorEntities))

            # find the arguments to the operator we've found (i.e., those
            # following the callsite)
            argsToOp, remainder = Formula._parseArgs(argString[nextCallLoc + 1:])
            print(operatorName, argsToOp)
            formulaArg = [Formula(Operator.get(operatorName), argsToOp)]

            print('r', argString + '\t' + repr(remainder))
            # find all arguments after the first found formula
            subsequentArgs, remainder = Formula._parseArgs(remainder)
            # instead of going to emptystring, maybe our remainder termination
            # condition could be contingent upon function depth?
            while remainder != '':
                moreSubsequentArgs, remainder = Formula._parseArgs(remainder)
                subsequentArgs.append(moreSubsequentArgs)

            # FIXME: This model doesn't work because we always assume our
            #        call goes to the end of the string (which it very well may
            #        not if we're an inner operator)
            # print(priorArgs, formulaArg, subsequentArgs)
            return priorArgs + formulaArg + subsequentArgs, ''
        else:
            # Either there is no next call or it's after the end of the current
            # one, so return all cell/literal args for this call and let
            # the caller deal with parsing whatever comes after
            remainingCallArgs = argString[:nextEndLoc]
            # # edge case -- same as before
            # if remainingCallArgs == '':
            #     return []
            # return remainingCallArgs.split(','), argString[nextEndLoc + 1:]
            remainingRes, _ = Formula._parseArgs(remainingCallArgs)
            # TODO: Handle commas more elegantly
            # If we have a leading comma on the remaining text, we need
            # to get rid of it or there will be an erroneous empty string arg
            postCallText = argString[nextEndLoc + 1:]
            if len(postCallText) > 0 and postCallText[0] == ',':
                postCallText = postCallText[1:]
            return remainingRes, postCallText

    # Takes an input string and attempts to turn it into a cell reference;
    # if it isn't a valid cell reference, returns the literal value instead
    @staticmethod
    def _getCellOrLiteral(text):
        try:
            cellRow = int(text[1:])
            cellCol = ord(text[0]) - ord('A')
            return Cell.get((cellRow, cellCol))
        except:
            # TODO: types
            return [text]

    @staticmethod
    def _nextToken(formulaString):
        nextOpen = formulaString.find('(')
        nextClose = formulaString.find(')')
        nextComma = formulaString.find(',')
        nonnegative = lambda x: x >= 0
        return min(filter(nonnegative, [nextOpen, nextClose, nextComma]))

    def evaluate(self):
        evaluatedOperands = []
        for operand in self.operands:
            if isinstance(operand, Formula):
                evaluatedOperands.append(operand.evaluate())
            elif isinstance(operand, Cell):
                evaluatedOperands.append(operand.value())
            else:
                # TODO: for now, we just assume it's an appropriate data type
                evaluatedOperands.append(int(operand))
        return self.operator.operate(evaluatedOperands)

    def __repr__(self):
        operandsStr = reduce(lambda acc, val: f'{acc}, {val}' if acc else val,
                             self.operands, '')
        return f'{self.operator.name}({operandsStr})'

# Test cases:
# Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, ADD(2, 3)), 2)')
# Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, ADD(3), 2)')
# Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, ADD(3))')
# Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9, 3)')
# Formula.fromText('=ADD(1, 2, AVERAGE(1, 3, 7, 6, 4, 2), 9)')
