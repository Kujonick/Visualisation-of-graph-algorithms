from algorythms.Algorythm import  PathSearch
from collections import deque


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
            self.write_change_visited(v,True)
            if t == v:
                break
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
        Q.append((s, None))
        parent = {}
        while Q:
            v, p= Q.pop()
            if self.nodes[v].visited:
                continue
            parent[v] = p
            self.write_change_visited(v,True)
            if t == v:
                break
            for u in self.nodes[v].edges:
                if not self.nodes[u].visited:
                    Q.append((u, v))
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
        
            
            

