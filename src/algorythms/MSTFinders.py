from algorythms.Algorythm import MSTSearch

class Kruskal(MSTSearch):
    def __init__(self, verticies):
        super().__init__(verticies)
        self.edges_uniqe = set()
        self.parent = {}
        self.rank = {}
        for v,node in self.nodes.items():
            self.change_value([node], v)
            self.parent[v] = v
            self.rank[v] = 1
            for _,edge in self.nodes[v].edges.items():
                self.edges_uniqe.add(edge)

        self.edges_uniqe = list(self.edges_uniqe)
        self.edges_uniqe.sort(key=lambda item:item.get_cost())

    def on_exit(self):
        for node in self.nodes.values():
            self.change_value([node],None)


    def start(self):
        mst_edges = []
        # print(self.parent)
        for edge in self.edges_uniqe:
            if len(mst_edges) == len(self.nodes) - 1:
                break
            self.write_selected_connections([edge.connection]+mst_edges)
            x = self.find(edge.origin.id)
            y = self.find(edge.end.id)
            if self.selectedID is not None:
                self.write_select(None)
            # print('  ',x,y)
            if x != y:
                mst_edges.append(edge.connection)
                self.union(x, y)
            
        # print(len(mst_edges))
        # print(mst_edges)
        self.write_selected_connections(mst_edges)


    def find(self,  id):
        if self.parent[id] != id:
            self.write_select(id)
            new_value = self.find(self.parent[id])
            if new_value != self.parent[id]:
                self.parent[id] = new_value
                self.write_change_value(id,new_value)
        return self.parent[id]

    def union(self, x, y):
        if self.rank[x] < self.rank[y]:
            self.parent[x] = y
            self.write_change_value(x,y)
        elif self.rank[x] > self.rank[y]:
            self.parent[y] = x
            self.write_change_value(y,x)
        else:
            self.parent[y] = x
            self.write_change_value(y,x)
            self.rank[x]+=1
