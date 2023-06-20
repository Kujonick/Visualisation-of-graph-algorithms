
import sys, os
module_path = os.path.abspath("src")

if module_path not in sys.path:
    sys.path.append(module_path)

from typing import List, Any, Tuple
from graphs import Node, Edge

# algorythm's steps
# one step = (function, (args), (prev, next))

class AlgorythmSteps:
    def __init__(self) -> None:
        self.steps : List[(function, Any, Any)] = []
        self.index = -1

    def add_step(self, func , args, states )-> None:
        self.index += 1
        self.steps.append((func, args, states))

    def pop_step(self) -> None:
        self.steps.pop()
    
    def clear_states(self) -> None:
        self.steps = []

    def check_next(self):
        return self.index < len(self.steps) - 1
    
    def check_prev(self):
        return self.index > -1
    
    def next_step(self) -> tuple:
        if self.index < len(self.steps) -1:
            self.index += 1 
            return self.steps[self.index]

    def to_last(self):
        while self.index < len(self.steps) -1:
            self.index += 1
            yield self.steps[self.index]
        return 

    def previous_step(self) -> tuple:
        if self.index > -1:
            self.index -= 1
            return self.steps[self.index+1]
    
    def to_first(self):
        while self.index > -1:
            yield self.steps[self.index]
            self.index -= 1
        return 
    
    def show_current_step(self):
        output = "START ->"
        if self.index > -1:
            x = self.steps[self.index-1]
            output = f"({x[0].__name__},{str(x[1])},{str(x[2])}) ->"
            if self.index > 0:
                x = self.steps[self.index]
                output = f"({x[0].__name__},{str(x[1])},{str(x[2])})" + output
        if self.index < len(self.steps) -1:
            x = self.steps[self.index+1]
            output = output + f" -> ({x[0].__name__},{str(x[1])},{str(x[2])})"
        print(output)
    
if __name__ == "__main__":
    Steps = AlgorythmSteps()
    def test_a():
        return 
    
    def test_b():
        return 
    
    Steps.add_step(test_a, (), (0, 1))
    Steps.show_current_step()
    assert(Steps.next_step() == (test_a,(), (0, 1)))
    Steps.add_step(test_b, (1), (2, 3))
    assert(Steps.next_step()== (test_b,(1), (2, 3)))
    assert(Steps.previous_step() == (test_b,(1), (2, 3)))
    assert(Steps.previous_step() == (test_a,(), (0, 1)))
