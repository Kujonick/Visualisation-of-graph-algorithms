import sys, os
module_path = os.path.abspath("src/algorythms")
sys.path.append(module_path)

from Algorythm import Algorytm



from collections import deque
class BFS (Algorytm):
    def __init__(self, verticies):
        super().__init__(self, verticies)

    def start(self, s :int, t : int):
        Q = deque()
        Q.append(s)
        while Q:
            v = Q.popleft()
            if self.nodes[v].visited:
                continue
            self.write_select(v)
            self.write_change_visited(v,True)
            for u in self.nodes[v].edges:
                if not self.nodes[u].visited:
                    Q.append(u)
            
            

