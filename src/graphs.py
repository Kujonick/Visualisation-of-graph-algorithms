from errors import WrongTypeConnect

class Node:

    def __init__(self, id : int, x : float, y : float) -> None:
        self.x = x          # Node position
        self.y = y          # (x,y)
        self.id = id        # identyfication number (one and only one for a graph)
        self.edges = dict()
        self.v = None       

    def __eq__(self, other) -> bool:
        if not isinstance(other,Node):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __str__(self) -> str:
        return f"P[{self.id}] ({self.x},{self.y})"

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def to_save(self) -> str:
        return f"{self.id} {self.x} {self.y}"
    
    def show(self):
        print(self)
        for k in self.edges.keys():
            edge : Edge = self.edges[k]
            print('|',edge)
        print('L----------------\n')
            
            
    # if connected returns Edge, else None. If argument provided is not Node or ID raise error
    def get_edge(self, other):
        if isinstance(other, Node):
            id = other.id
        elif isinstance(other, int):
            id = other
        else:
            raise TypeError 

        return self.edges.get(id, None)
    
    # adds new Edge to Node.edges.  Returns False if nothing's changed
    def connect(self, other, directed : bool, maxflow :int=None, minflow:int=None, cost:int = None) -> bool:
        if not isinstance(other,Node):
            raise WrongTypeConnect
        
        
        if self.get_edge(other) != None:    # Edge already exists
            return False
        
        
        if not directed and other.get_edge(self) != None:  # Edge of undirected graph shan't be connected to Node which has already directed Edge to this one 
            return False                                        # It should not accur frequently, but must be handled
        

        edge = Edge(self, other, directed, maxflow=maxflow, minflow=minflow, cost=cost)
        self.edges[other.id] = edge  
        if not directed:
             other.edges[self.id] = edge
        
        return True
    
    # deletes Edge in .edges
    def disconnect(self, other) -> bool:

        if not isinstance(other,Node):
            raise WrongTypeConnect
        
        edge = self.get_edge(other)
        if edge != None:    # Edge from self to other exists
            del self.edges[other.id]
            if not edge.directed:
                del other.edges[other.id]
            return True
        return False        

        


class Edge:

    def __init__(self, node1 :Node, node2 :Node, directed :bool, maxflow :int=None , 
                 flow=0, minflow:int=None, cost:int = None ) -> None:
        self.origin = node1
        self.end = node2
        self.directed = directed
        self.maxflow = maxflow
        self.flow = flow
        self.minflow = minflow
        self.cost = cost

    def __hash__(self) -> int:
        return 3*hash(self.origin) + hash(self.end)
    
    def __eq__(self,other) -> bool:
        if not isinstance(other,Edge):
            return False
        other : Edge
        if other.directed != self.directed:
            return False
        if self.directed:
            return self.origin.id == other.origin.id and self.end.id == other.end.id
        return (self.origin.id == other.origin.id and self.end.id == other.end.id) or self.origin.id==other.end.id and self.end.id == other.origin.id
    
    def __str__(self) -> str:
        if self.directed:
            arrow = '->'
        else:
            arrow = '--'
        return (f" {self.origin.id} {arrow} {self.end.id}    {self.minflow}/ {self.flow} /{self.maxflow}   c:{self.cost}")

    def get_flow(self) -> int:
        return self.flow
    
    def change_flow_to(self, flow) -> None:
        self.flow = flow

    def change_flow(self, change) -> None:
        if self.maxflow != None and self.flow + change > self.maxflow:
            return OverflowError
        self.flow += change

    def set_maxflow(self, value :int) -> None:
        if not isinstance(value, int):
            raise ValueError
        self.maxflow = value

    def get_cost(self) -> int:
        return self.cost
    
    def set_cost(self, value:int) -> None:
        if not isinstance(value, int):
            raise ValueError
        self.cost = value
    
    # changes Edge to undirected, if there is another in opposite direction, both are merged
    def change_to_undirected(self) -> None:
        if not self.directed:
            return
        origin = self.origin
        end = self.end
        edge : Edge= end.get_edge(origin) 
        
        
        if edge != None:        #checks if is other way Edge present

            if self.maxflow == None and edge.maxflow != None:   #checks if is other way Edge present
                    self.maxflow = edge.maxflow
            elif edge.maxflow != None:
                self.maxflow = min(self.maxflow, edge.maxflow)

            #---- w dalekiej przyszłości ----#
            if self.minflow == None and edge.minflow != None:
                self.minflow = edge.minflow
            elif edge.minflow != None:
                self.minflow = min(self.minflow, edge.minflow)

            del end.edges[self.origin.id]
        self.directed = False
        end.edges[self.origin.id] = self

    # changes Edge to directed
    def change_to_directed(self) -> None:
        if self.directed:
            return
        del self.end.edges[self.origin.id]
        self.directed = True

    # Returns True if there's no edge in other direction between these two nodes
    def can_be_reversed(self) -> bool:
        if not self.directed:
            return False
        
        end = self.end
        if end.get_edge(self.origin.id) != None:
            return False
        return True
    
    # changes direction of Edge, return False on failure
    def reverse(self) -> bool:
        if not self.can_be_reversed():
            return False
        origin = self.origin
        end = self.end
        del self.origin.edges[end.id]
        end.edges[origin.id] = self
        self.origin, self.end = self.end, self.origin
        return True
            
    # function return string which contains edge saving 
    def to_save(self) -> str:
        return f"{self.origin.id} {self.end.id} {1 if self.directed else 0} {self.maxflow} {self.minflow} {self.cost}"


if __name__ == "__main__":
    def directed_change_test(prints = False):
        L = [Node(0,2,0),Node(1,2,1)]
        L[0].connect(L[1],False, maxflow=10)
        print("\n##### direction change test")
        if prints:
            print("### Before change")
            for v in L:
                v.show()
        e : Edge= L[0].get_edge(1)
        e.change_to_directed()
        if prints:
            print("### After change")
            for v in L:
                v.show()
        L[1].connect(L[0], True, 5)
        if prints:
            print("### After additional edge")
            for v in L:
                v.show()
        e.change_to_undirected()
        if prints:
            print("### After second change")
            for v in L:
                v.show()
        print(len(L[0].edges) == 1)
        print(len(L[1].edges) == 1)
        print(L[0].get_edge(L[1]).maxflow == 5)
        print(L[1].get_edge(L[0]).maxflow == 5)

    def edge_properties_test():
        print("\n##### edge properties test")
        n1, n2 = Node(0,0,0), Node(1,0,1)
        n1.connect(n2, True)
        e:Edge = n1.get_edge(n2)
        print("basic:        ",e)
        e.change_flow_to(5)
        print("changed flow: ",e)
        e.change_flow(-2)
        print("lowered flow: ",e)
        e.set_maxflow(8)
        print("set maxflow:  ",e)
        e.set_cost(3)
        print("set cost:     ",e)
        e.reverse()
        print("reversed:     ",e)
        n1.connect(n2, True)
        e.reverse()
        print("can't reverse:",e)
        n1.show()
        n2.show()

    directed_change_test()
    edge_properties_test()
