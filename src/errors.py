
# Raised while trying to connect Node to notNode object
class WrongTypeConnect (Exception):
    def __init__(self, element):
        self.message = f"Connection is allowed only between Nodes, not Node and {type(element).__name__}"
        super().__init__(self.message)

#Raised while reading a file
class FileReadError (Exception):
    def __init__(self, filename : str, line : int):
        self.message = f"File {filename} couldn't be read on line {line}"
        super().__init__(self.message)