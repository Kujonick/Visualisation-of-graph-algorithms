
import sys, os
module_path = os.path.abspath("src")

if module_path not in sys.path:
    sys.path.append(module_path)

from typing import List, Any, Tuple, Sequence
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
    
    def _step_to_string(self,step):
        if step[1] != None:
            x = ' '+ ' '.join(str(e) for e in step[1])
        else:
            x = 'None'
        y = ''
        for state in step[2]:
            if issubclass(type(state),Sequence):
                y = y+'{\n'+ '\n'.join(str(e) for e in state) + ' }'
            else:
                y = y +' '+ str(state)

        return f"({step[0].__name__},{x},{y})"

    def show_current_step(self):
        print(f"{self.index} / {len(self.steps) -1 }")
        output = " EMPTY "
        if self.index > -1:
            output = self._step_to_string(self.steps[self.index]) + ' |'
            if self.index > 0:
                output = f"{self._step_to_string(self.steps[self.index-1])} > {output}"
        if self.index < len(self.steps) -1:
            output = f"{output} >> {self._step_to_string(self.steps[self.index+1])}"
        print(output)
    
if __name__ == "__main__":
    Steps = AlgorythmSteps()
    def test_a():
        return 
    
    def test_b():
        return 
    
    Steps.add_step(test_a, [], (0, 1))
    Steps.show_current_step()
    assert(Steps.previous_step() == (test_a,[], (0, 1)))
    Steps.next_step()
    Steps.add_step(test_b, [1], (2, 3))
    assert(Steps.previous_step() == (test_b,[1], (2, 3)))
    assert(Steps.previous_step() == (test_a,[], (0, 1)))
