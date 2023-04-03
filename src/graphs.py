from errors import *

class Node:

    
    def __init__(self, x : float, y : float, id : int) -> None:
        self.x = x          # Node position
        self.y = y          # (x,y)
        self.id = id        # identyfication number (one and only one for a graph)
        self.edges = dict()

    def __eq__(self, other) -> bool:
        if not isinstance(other,Node):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __str__(self) -> str:
        return f"P[{self.id}]({self.x},{self.y}"
    
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
    def connect(self, other, directed : bool) -> bool:
        if not isinstance(other,Node):
            raise WrongTypeConnect
        
        
        if self.get_edge(other) != None:    # Edge already exists
            return False
        
        
        if directed != False and other.get_edge(self) != None:  # Edge of undirected graph shan't be connected to Node which has already directed Edge to this one 
            return False                                        # It should not accur frequently, but must be handled
        

        edge = Edge(self, other, directed)
        self.edges[other.id] = edge  
        if not directed:
             other.edges[self.id] = edge
        
        return True
        

        


class Edge:


    def __init__(self, node1, node2, directed, maxflow=None, flow=0, minflow=None) -> None:
        self.origin = node1
        self.end = node2
        self.directed = directed
        self.maxflow = maxflow
        self.flow = flow
        self.minflow = minflow

    def __hash__(self) -> int:
        return 3*hash(self.origin) + hash(self.end)
    

    def change_flow(self, change) :
        self.flow += change

    def change_to_directed(self) -> None:
        if self.directed:
            return
        v = self.origin
        u = self.end
        if u.get_edge()