class Node:
    def __init__(self, x, y, idx) -> None:
        self.x = x
        self.y = y
        self.idx = idx

    def __eq__(self, other) -> bool:
        if not isinstance(other,Node):
            return False
        return self.idx == other.idx
    
    def __hash__(self) -> int:
        return hash(self.idx)
    
    def __str__(self) -> str:
        return f"P[{self.idx}]({self.x},{self.y}"
    
    def connect(self, other) -> None:
        pass