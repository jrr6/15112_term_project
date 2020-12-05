# utils
# Joseph Rotella (jrotella, F0)
#
# Contains miscellaneous utility code.

def splitEscapedString(string, delimiter):
    result = []
    startIdx = 0
    curIdx = 1
    while curIdx < len(string):
        if string[curIdx] == delimiter and string[curIdx - 1] != '\\':
            result.append(string[startIdx:curIdx])
            startIdx = curIdx + 1
        curIdx += 1
    if startIdx != curIdx:
        result.append(string[startIdx:curIdx])
    return result
