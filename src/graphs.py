class Node:
    def __init__(self, x, y, idx) -> None:
        self.x = x
        self.y = y
        self.idx = idx
        self.edges = dict()

    def __eq__(self, other) -> bool:
        if not isinstance(other,Node):
            return False
        return self.idx == other.idx
    
    def __hash__(self) -> int:
        return hash(self.idx)
    
    def __str__(self) -> str:
        return f"P[{self.idx}]({self.x},{self.y}"
    
    # adds to 
    def connect(self, other) -> None:
        pass

class Edge:
    def __init__(self, node1, node2, directed, maxflow = None, flow = 0, minflow = None) -> None:
        self.origin = node1
        self.end = node2
        self.directed = directed
        self.maxflow = maxflow
        self.flow = flow
        self.minflow = minflow

    def change_flow(self, change) :
        self.flow += change
