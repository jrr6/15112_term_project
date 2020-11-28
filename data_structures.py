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

# A bare-bones graph data structure sufficient for tracking formula dependencies
class DependencyGraph(object):
    def __init__(self):
        self.vertices = {}

    def addDependencies(self, vertex, dependencies):
        if vertex not in self.vertices:
            self.vertices[vertex] = set()

        for dependency in dependencies:
            if dependency not in self.vertices:
                self.vertices[dependency] = set()
            self.vertices[dependency].add(vertex)

    # removes all dependencies of a single vertex
    def removeDependencies(self, vertex):
        if vertex in self.vertices:
            del self.vertices[vertex]

    # removes a vertex and all references thereto from the graph
    def removeVertex(self, vertex):
        for otherVertex in self.vertices:
            if vertex in otherVertex:
                otherVertex.remove(vertex)
        if vertex in self.vertices:
            del self.vertices[vertex]

    # returns all dependents (and dependents-of-dependents, and recursively
    # forth) of this vertex
    def getDependents(self, vertex):
        if vertex not in self.vertices:
            return set()
        if len(self.vertices[vertex]) == 0:
            return set()
        dependents = self.vertices[vertex]
        for dependent in self.vertices[vertex]:
            dependents = dependents.union(self.getDependents(dependent))
        return dependents
