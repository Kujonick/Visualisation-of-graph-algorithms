import sys, os
module_path = os.path.abspath("src/algorythms")
sys.path.append(module_path)

from Algorythm import Algorytm
from collections import deque
class PathSearch (Algorytm):
    def __init__(self, verticies):
        super().__init__(verticies)
        self.parameters_name = ["s","t"]
        self.parameters = {}

    def get_parameters_name(self):
        return self.parameters_name
    
    def set_parameters(self, parameter, value):
        self.parameters[parameter] = value
    
    def constrains(self, parameter, value):
        if parameter == 's':
            return self.nodes.get(value, None) != None
        if parameter == 't':
            return self.nodes.get(value, None) != None and value != self.parameters['s']
        return False

class BFS (PathSearch):
    def __init__(self, verticies):
        super().__init__(verticies)

    def start(self):
        s = self.parameters["s"]
        t = self.parameters["t"]
        Q = deque()
        Q.append(s)
        parent = {}
        while Q:
            v = Q.popleft()
            if self.nodes[v].visited:
                continue
            self.write_select(v)
            if t == v:
                self.write_select(None)
                break
            self.write_change_visited(v,True)
            for u in self.nodes[v].edges:
                if not self.nodes[u].visited:
                    if parent.get(u,None) == None:
                        parent[u] = v
                    Q.append(u)
        else:
            return
        line = []
        v = t
        print(parent)
        while v != s:
            p = parent[v]
            line.append(self.verticies[p].get_connection(self.verticies[v]))
            v = p
        self.write_selected_connections(line)


class DFS (PathSearch):
    def __init__(self, verticies):
        super().__init__(verticies)

    def start(self):
        s = self.parameters["s"]
        t = self.parameters["t"]
        Q = deque()
        Q.append(s)
        parent = {}
        while Q:
            v = Q.pop()
            if self.nodes[v].visited:
                continue
            self.write_select(v)
            if t == v:
                self.write_select(None)
                break
            self.write_change_visited(v,True)
            for u in self.nodes[v].edges:
                if not self.nodes[u].visited:
                    if parent.get(u,None) == None:
                        parent[u] = v
                    Q.append(u)
        else:
            return
        line = []
        v = t
        print(parent)
        while v != s:
            p = parent[v]
            line.append(self.verticies[p].get_connection(self.verticies[v]))
            v = p
        self.write_selected_connections(line)
        
            
            

