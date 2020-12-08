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

# A bare-bones "graph" for representing formula dependency relationships
class DependencyGraph(object):
    def __init__(self):
        self.dependents = {}
        self.dependencies = {}

    def setDependencies(self, cellRef, dependencies: set):
        if cellRef not in self.dependencies:
            # we could just use the dependencies param, but that's pass-by-ref,
            # and who knows what the caller might do with it...
            self.dependencies[cellRef] = set()

        oldDependencies = self.dependencies[cellRef]

        # If there were any old dependencies the cell no longer has, remove them
        for oldDependency in oldDependencies - dependencies:
            self.dependents[oldDependency].remove(cellRef)
            self.dependencies[cellRef].remove(oldDependency)

        # Add all new dependencies (but don't re-add ones that already exist)
        for dependency in dependencies - oldDependencies:
            if dependency not in self.dependents:
                self.dependents[dependency] = set()

            self.dependents[dependency].add(cellRef)
            self.dependencies[cellRef].add(dependency)

        # If this cell has no deps or isn't anyone's dep, remove to save space
        if len(self.dependencies[cellRef]) == 0:
            del self.dependencies[cellRef]
        if cellRef in self.dependents and len(self.dependents[cellRef]) == 0:
            del self.dependents[cellRef]

    def getDependents(self, cellRef):
        if cellRef not in self.dependents:
            return set()

        dependents = self.dependents[cellRef]
        for dependent in dependents:
            # we catch infinite recursion only at runtime -- don't do it here!
            if dependent is not cellRef:
                dependents = dependents.union(self.getDependents(dependent))
        return dependents

    # Gets only the first layer of dependencies of a given cell
    def getShallowDependencies(self, cellRef):
        return self.dependencies.get(cellRef, set())
