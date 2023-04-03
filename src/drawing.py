import sys
from graphs import Node
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsTextItem, \
    QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt


class Vertex(QGraphicsEllipseItem):
    def __init__(self, node):
        super(Vertex, self).__init__(node.x, node.y, 30, 30)

        # Remember initial position of vertex for mouseReleaseEvent
        self.initial_x = node.x
        self.initial_y = node.y

        # Set the pen and brush for the vertex
        pen = QPen(Qt.black)
        brush = QBrush(QColor(194, 223, 255))
        self.setPen(pen)
        self.setBrush(brush)

        # Make the vertex movable
        self.setFlag(self.ItemIsMovable)

        # Store a reference to the Node object
        self.node = node

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.node.update_position(self.initial_x + self.x(), self.initial_y + self.y())

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create a QGraphicsScene to hold the nodes
        self.scene = QGraphicsScene()

        # Create a QGraphicsView to display the scene
        self.view = QGraphicsView(self.scene)

        # Set the window properties
        self.setWindowTitle("Node Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Add the view to the window
        self.setCentralWidget(self.view)

        # example nodes
        nodes = []
        nodes.append(Node(100, 100, 0))
        nodes.append(Node(200, 200, 1))
        nodes.append(Node(300, 100, 2))
        nodes[0].connect(nodes[1], False)
        nodes[1].connect(nodes[2], False)
        nodes[2].connect(nodes[0], False)

        # Add the nodes to the scene
        for node in nodes:
            self.scene.addItem(self.create_vertex(node))

    def create_vertex(self, node):
        # Create a QGraphicsTextItem to hold the node index
        text = QGraphicsTextItem(str(node.id))

        # Create a vertex to represent the node
        vertex = Vertex(node)

        # Add the text to the vertex
        text.setParentItem(vertex)
        text.setPos(node.x + 7, node.y + 1)

        # Return the vertex
        return vertex


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
