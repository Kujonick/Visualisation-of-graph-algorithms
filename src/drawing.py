import sys
import math
from graphs import Node
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsTextItem, \
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QGraphicsPolygonItem
from PyQt5.QtGui import QPen, QBrush, QColor, QPolygonF, QTransform
from PyQt5.QtCore import Qt, QPointF, QLineF


class Vertex(QGraphicsEllipseItem):
    def __init__(self, node):
        super().__init__(node.x, node.y, 34, 34)

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

        # Store edges of the Vertex
        self.edges = []

    def add_connection(self, edge):
        self.edges.append(edge)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        for edge in self.edges:
            edge.adjust()
        self.node.update_position(self.initial_x + self.x(), self.initial_y + self.y())


class Connection(QGraphicsLineItem):
    def __init__(self, origin, end, directed):
        super().__init__(origin.initial_x + 17, origin.initial_y + 17, end.initial_x + 17, end.initial_y + 17)
        self.origin = origin
        self.end = end
        self.directed = directed
        self.arrowhead = None

    def adjust(self):
        start_pos = QPointF(self.origin.initial_x + self.origin.x() + 17, self.origin.initial_y + self.origin.y() + 17)
        end_pos = QPointF(self.end.initial_x + self.end.x() + 17, self.end.initial_y + self.end.y() + 17)
        line = QLineF(start_pos, end_pos)
        self.setLine(line)

        if self.directed:
            self.arrowhead.adjust(self)

    def set_arrowhead(self, arrowhead):
        self.arrowhead = arrowhead


class Arrowhead(QGraphicsPolygonItem):
    def __init__(self, line):
        super().__init__()
        self.adjust(line)

    def adjust(self, line):
        origin_vertex_x = line.origin.x() + line.origin.initial_x
        end_vertex_x = line.end.x() + line.end.initial_x
        origin_vertex_y = line.origin.y() + line.origin.initial_y
        end_vertex_y = line.end.y() + line.end.initial_y

        dx, dy = origin_vertex_x - end_vertex_x, origin_vertex_y - end_vertex_y
        length = math.sqrt(dx**2 + dy**2)
        norm_x, norm_y = dx/length, dy/length
        perp_x, perp_y = -norm_y, norm_x

        left_x = end_vertex_x + 5 * norm_x + 15 * perp_x
        left_y = end_vertex_y + 5 * norm_y + 15 * perp_y

        right_x = end_vertex_x + 5 * norm_x - 15 * perp_x
        right_y = end_vertex_y + 5 * norm_y - 15 * perp_y

        left_point = QPointF(left_x, left_y)
        right_point = QPointF(right_x, right_y)
        end_point = QPointF(end_vertex_x, end_vertex_y)
        self.setPolygon(QPolygonF([left_point, end_point, right_point]))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
        nodes = [Node(0, 100, 100), Node(10, 200, 200), Node(222, 300, 100)]
        nodes[0].connect(nodes[1], False)
        nodes[0].connect(nodes[2], False)
        nodes[2].connect(nodes[1], False)

        # Create a dictionary to store vertex objects
        self.vertices = {}

        # Add the nodes to the scene
        for node in nodes:
            vertex = self.create_vertex(node)
            self.scene.addItem(vertex)
            self.vertices[node.id] = vertex
        for node in nodes:
            for edge in node.edges.values():
                self.scene.addItem(self.create_edge(edge))

    def create_vertex(self, node):
        # Create a QGraphicsTextItem to hold the node index
        text = QGraphicsTextItem(str(node.id))

        # Create a vertex to represent the node
        vertex = Vertex(node)

        # Add the text to the vertex
        text.setParentItem(vertex)
        text_rect = text.boundingRect()
        text.setPos(node.x - text_rect.width() / 2 + 17, node.y - text_rect.height() / 2 + 17)

        vertex.setZValue(1)

        # Add the vertex to dictionary and return it
        self.vertices[node.id] = vertex
        return vertex

    def create_edge(self, edge):
        # Create an edge to represent the connection between two vertices
        origin_vertex = self.vertices[edge.origin.id]
        end_vertex = self.vertices[edge.end.id]
        line = Connection(origin_vertex, end_vertex, edge.directed)

        # Set the pen for the edge
        pen = QPen(Qt.black)
        pen.setWidth(2)
        line.setPen(pen)

        # if edge is directed - add arrowhead
        if edge.directed:
            self.create_arrowhead(line)

        # Add the edge to the origin/end vertex's edges list
        origin_vertex.add_connection(line)
        end_vertex.add_connection(line)

        # Return the edge
        return line

    def create_arrowhead(self, line):
        # Create Arrowhead object
        arrowhead = Arrowhead(line)

        # Set Pen & Brush
        arrowhead.setPen(QPen(Qt.black))
        arrowhead.setBrush(QBrush(Qt.black))

        # Attach arrowhead to line
        line.set_arrowhead(arrowhead)
        self.scene.addItem(arrowhead)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
