from typing import List, Any, Tuple
from graphs import Node, Edge

# algorythm's steps
# one step = (function, (args), (prev, next))

class AlgorythmSteps:
    def __init__(self) -> None:
        self.steps : List[(function, Any, Any)] = []
        self.index = -1

    def add_step(self, func , args, states )-> None:
        self.steps.append((func, args, states))

    def pop_step(self) -> None:
        self.steps.pop()
    
    def clear_states(self) -> None:
        self.steps = []

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

if __name__ == "__main__":
    Steps = AlgorythmSteps()
    def test_a():
        return 
    
    def test_b():
        return 
    
    Steps.add_step(test_a, 0, 1)
    assert(Steps.next_step() == (test_a, 1))
    Steps.add_step(test_b, 2, 3)
    assert(Steps.next_step()== (test_b, 3))
    assert(Steps.previous_step() == (test_b, 2))
    assert(Steps.previous_step() == (test_a, 0))
