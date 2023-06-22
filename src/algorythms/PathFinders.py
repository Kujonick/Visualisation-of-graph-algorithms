from algorythms.Algorythm import PathSearch
from heapq import heapify, heappop, heappush, heappushpop, heapreplace

class Dijkstra(PathSearch):


    def __init__(self, verticies):
        super().__init__(verticies)
        for node in self.nodes.values():
            self.change_value([node], float('inf'))

    def check_graph(verticies):
        x = True if len(verticies) > 0 else "Empty Graph"
        if x is True:
            for vert in verticies.values():
                for edge in vert.node.edges.values():
                    if edge.get_cost() < 0:
                        return "All edges are needed to be non negative"
            return True
        return x
    
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
        if self.nodes[t].value == float('inf'):
            return
        line = []
        v = t
        while v != s:
            p = parent[v]
            line.append(self.verticies[p].get_connection(self.verticies[v]))
            v = p
        self.write_selected_connections(line)       
    
    def on_exit(self):
        super().on_exit()
        for node in self.nodes.values():
            self.change_value([node], None)



class BellmanFord(PathSearch):


    def _convert_value(self, v):
        return f"{self.values[v]} p:{self.parent[v]}"
    
    def __init__(self, verticies):
        super().__init__(verticies)
        self.parent = {}
        self.values = {}
        self.edges = set()
        for v, node in self.nodes.items():
            self.parent[v] = None
            self.values[v] = float('inf')
            self.change_value([node], self._convert_value(v))
            self.edges.update(node.edges.values())
        self.edges = list(self.edges)

    def _relax(self, edge):
        v = edge.end.id
        u = edge.origin.id
        if self.values[v] > self.values[u] + edge.cost:
            self.write_select(edge.end)
            self.parent[v] = u
            self.values[v] = self.values[u] + edge.cost
            self.change_value([edge.end], self._convert_value(v))

        
        elif not edge.directed:
            self.write_select(edge.origin.id)
            if self.values[u] > self.values[v] + edge.cost:
                self.parent[u] = v
                self.values[u] = self.values[v] + edge.cost
                self.change_value([edge.end], self._convert_value(u))


    def start(self):
        s = self.parameters["s"]
        t = self.parameters["t"]
        self.values[s] = 0
        self.change_value([self.nodes[s]], self._convert_value(s))
        for _ in range(len(self.nodes) -1 ):
            for edge in self.edges:
                self.write_selected_connections([edge.connection])
                self._relax(edge)



        if self.nodes[t].value == float('inf'):
            return
        line = []
        v = t
        while v != s:
            p = self.parent[v]
            line.append(self.verticies[p].get_connection(self.verticies[v]))
            v = p
        self.write_selected_connections(line)  
    
    def on_exit(self):
        for node in self.nodes.values():
            self.change_value([node], None)
