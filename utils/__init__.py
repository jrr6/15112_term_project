# utils
# Joseph Rotella (jrotella, F0)
#
# Contains miscellaneous utility code.

# Splits a string along a delimiter, ignoring backslash-escaped delimiters.
# Note: does NOT de-escape escaped delimiters.
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
