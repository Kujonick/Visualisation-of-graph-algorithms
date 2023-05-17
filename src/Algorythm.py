from algorythmSteps import AlgorythmSteps
from drawing import Vertex, Connection
from graphs import Node, Edge
from typing import Set
class Algorytm:
    def __init__(self, verticies):
        self.steps = AlgorythmSteps()
        self.verticies : dict[int : Vertex]= verticies
        self.nodes : dict[int : Node]= {i : self.verticies[i].node for i in verticies}
        self.selectedID : int = None

    def change_visited(self, args, state):
        node : Node = args[0]
        node.change_visited(state)
        self.verticies[node.id].changed_visited()

    def change_value(self, args, value):
        node : Node = args[0]
        node.change_value(value)
        self.verticies[node.id].changed_value()

    def selection(self, args, next : int ):
        if self.selectedID != None:
            self.verticies[self.selectedID].set_unselected()
        if next != None:
            self.verticies[next].set_selected()
        self.selectedID = next
    

    #-------------------------------

    def write_change_visited(self, node : Node, state ):
        if isinstance(node, int):
            node = self.nodes.get(node)
        prev = node.visited
        self.change_visited(node, state)
        self.steps.add_step(self.change_visited,(node), (prev, state))

    def write_change_value(self, node : Node, value ):
        if isinstance(node, int):
            node = self.nodes.get(node)
        prev = node.value
        self.change_value(node, value)
        self.steps.add_step(self.change_value,(node) ,(prev, value))
        
    
    def write_select(self, node : int):
        if isinstance(node, Node):
            node = node.id
        self.steps.add_step(self.selection,None, (self.selectedID, node))
        self.selection(None, node)
    




            
        
