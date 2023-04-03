
# Raised when 
class WrongTypeConnect (Exception):
    def __init__(self, element):
        self.message = f"Connection is allowed only between Nodes, not Node and {type(element).__name__}"
        super().__init__(self.message)