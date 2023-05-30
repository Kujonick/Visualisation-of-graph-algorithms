
import sys, os
module_path = os.path.abspath("src")

# Dodaj ścieżkę do sys.path
sys.path.append(module_path)

from algorythmSteps import AlgorythmSteps
#from drawing import Vertex, Connection
from graphs import Node, Edge

class Algorytm:
    def __init__(self, verticies):
        self.steps = AlgorythmSteps()
        self.verticies = verticies
        self.nodes : dict[int : Node]= {i : self.verticies[i].node for i in verticies}
        self.selectedID : int = None

    # Vericies
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
    
    # Edges
    def change_flow(self, args, next_flow : int):
        edge : Edge = args[0]
        edge.change_flow_to(next_flow)
        edge.connection.uptade_cost()
    #-------------------------------

    def write_change_visited(self, node : Node, state ):
        if isinstance(node, int):
            node = self.nodes.get(node)
        prev = node.visited
        self.change_visited((node), state)
        self.steps.add_step(self.change_visited,(node), (prev, state))
        

    def write_change_value(self, node : Node, value ):
        if isinstance(node, int):
            node = self.nodes.get(node)
        prev = node.value
        self.change_value((node), value)
        self.steps.add_step(self.change_value,(node) ,(prev, value))
        
    
    def write_select(self, node : int):
        if isinstance(node, Node):
            node = node.id
        self.selection(None, node)
        self.steps.add_step(self.selection,None, (self.selectedID, node))
        
    
    # Edges

    def write_change_flow(self, edge : Edge, value):
        prev = edge.flow
        if value > edge.maxflow:
            raise ValueError("Wrong flow value > maxflow")
        self.change_flow((edge), value)
        self.steps.add_step(self.change_flow,(edge) ,(prev, value))

    # Using

    def next(self):
        x = self.steps.next_step()
        if x == None:
            return
        f, args, states = x
        f(args, states[1])
    
    def prev(self):
        x = self.steps.previous_step()
        if x == None:
            return
        f, args, states = x
        f(args, states[0])

    def to_first(self):
        for x in self.steps.to_first():
            x = self.steps.previous_step()
            if x == None:
                return
            f, args, states = x
            f(args, states[0])

    def to_last(self):
        for x in self.steps.to_last():
            x = self.steps.previous_step()
            if x == None:
                return
            f, args, states = x
            f(args, states[0])
            
        
