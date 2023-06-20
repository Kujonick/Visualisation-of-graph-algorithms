import sys, os
module_path = os.path.abspath("src/algorythms")
sys.path.append(module_path)

from Algorythm import PathSearch
from heapq import heapify, heappop, heappush, heappushpop, heapreplace

class Dijkstra(PathSearch):
    def __init__(self, verticies):
        super().__init__(verticies)
        for node in self.nodes.values():
            self.change_value([node], float('inf'))

    def start(self):
        s = self.parameters["s"]
        t = self.parameters["t"]
        self.change_value([self.nodes[s]],0)
        Q = [(0,s, None)]
        parent = {}
        while Q:
            value, v, p = heappop(Q)
            if self.nodes[v].visited:
                continue
            parent[v] = p
            self.write_change_visited(v, True)
            if t == v:
                break
            for u,edge in self.nodes[v].edges.items():
                if not self.nodes[u].visited:
                    self.write_select(u)
                    if self.nodes[u].value > value + edge.get_cost():
                        self.write_change_value(u, value + edge.get_cost())
                        heappush(Q, (value + edge.get_cost(),u, v))
            self.write_select(None)
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
    
