from algorythms.Algorythm import MSTSearch

class Kruskal(MSTSearch):
    def __init__(self, verticies):
        super().__init__(verticies)
        self.edges_uniqe = set()
        self.parent = []
        self.rank = []
        for v,node in self.nodes.items():
            self.rank.append(0)
            self.parent.append(v)
            for w,edge in self.nodes[v].edges.items():
                self.edges_uniqe.add(edge)

        self.edges_uniqe = list(self.edges_uniqe)
        self.edges_uniqe.sort(key=lambda item:item.get_cost())


    def start(self):
        mst_edges = []
        for edge in self.edges_uniqe:
            if len(mst_edges) == len(self.nodes) - 1:
                break
            x = self.find(edge.origin.id)
            y = self.find(edge.end.id)
            if x != y:
                mst_edges.append(self.verticies[x].get_connection(self.verticies[y]))
                self.union(x, y)

        self.write_selected_connections(mst_edges)


    def find(self,  node):
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def union(self, x, y):
        if self.rank[x] < self.rank[y]:
            self.parent[x] = y
        elif self.rank[x] > self.rank[y]:
            self.parent[y] = x
        else:
            self.parent[y] = x
            self.rank[x]+=1
