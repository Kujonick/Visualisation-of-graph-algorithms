#
import sys
from graphs import Node
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsTextItem, \
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem, QGraphicsPolygonItem, QPushButton, QGridLayout, QWidget
from PyQt5.QtGui import QPen, QBrush, QColor, QPolygonF, QTransform, QPainter
from PyQt5.QtCore import Qt, QPointF, QLineF, QEvent, QObject, pyqtSignal, pyqtSlot

modes = {
    "Add Vertex": False,
    "Delete Vertex/Edge": False
}

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

        # Set signal in case of removal

    def add_connection(self, edge):
        self.edges.append(edge)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        for edge in self.edges:
            edge.adjust()

        self.node.update_position(self.initial_x + self.x(), self.initial_y + self.y())

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and modes["Delete Vertex/Edge"]:
            for edge in self.edges:
                self.scene().removeItem(edge)
                del edge

            self.edges.clear()
            self.scene().vertex_deleted_sig.emit(self.node.id)
            self.scene().removeItem(self)
            del self


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

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and modes["Delete Vertex/Edge"]:
            self.origin.edges.remove(self)
            self.end.edges.remove(self)
            self.scene().removeItem(self)
            del self


class GraphicsScene(QGraphicsScene):
    vertex_deleted_sig = pyqtSignal(int)
    vertex_add_sig = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and modes["Add Vertex"]:

            self.vertex_add_sig.emit((event.scenePos().x() - 17, event.scenePos().y() - 17))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize Graph #

        # Create a QGraphicsScene to hold the nodes and connect signals
        self.scene = GraphicsScene()
        self.scene.vertex_deleted_sig.connect(self.delete_vertex)
        self.scene.vertex_add_sig.connect(self.add_vertex)

        # Create a QGraphicsView to display the scene
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing)
        self.installEventFilter(self.view)
        # Set the window properties
        self.setWindowTitle("Node Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Add the view to the window
        self.setCentralWidget(self.view)

        # example nodes
        nodes = [Node(0, 100, 100), Node(1, 200, 200), Node(2, 300, 100)]
        nodes[0].connect(nodes[1], False)
        nodes[0].connect(nodes[2], False)
        nodes[2].connect(nodes[1], False)

        # Create a dictionary to store vertex objects
        self.vertices = {}

        # Add the nodes to the scene
        for node in nodes:
            vertex = self.create_vertex(node)
            self.scene.addItem(vertex)
        for node in nodes:
            for edge in node.edges.values():
                self.scene.addItem(self.create_edge(edge))

        # Initialize UI #

        # Create grid and buttons
        grid = QGridLayout(self.view)
        self.delete_mode_button = QPushButton("Delete Vertex/Edge", self)
        self.delete_mode_button.clicked.connect(self.buttons_handler)
        self.add_vertex_mode_button = QPushButton("Add Vertex", self)
        self.add_vertex_mode_button.clicked.connect(self.buttons_handler)

        grid.addWidget(self.delete_mode_button, 0, 0, Qt.AlignLeft | Qt.AlignBottom)
        grid.addWidget(self.add_vertex_mode_button, 0, 1, Qt.AlignLeft | Qt.AlignBottom)
        grid.setColumnStretch(3, 1)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)

    def create_vertex(self, node):
        # Create a QGraphicsTextItem to hold the node index
        text = QGraphicsTextItem(str(node.id))

        # Create a vertex to represent the node
        vertex = Vertex(node)
        # vertex.deleted.connect(self.delete_vertex)

        # Add the text to the vertex
        text.setParentItem(vertex)
        text_rect = text.boundingRect()
        text.setPos(node.x - text_rect.width() / 2 + 17, node.y - text_rect.height() / 2 + 17)

        vertex.setZValue(1)

        # Add the vertex to dictionary and return it
        self.vertices[node.id] = vertex
        return vertex

    @pyqtSlot(int)
    def delete_vertex(self, node_id):
        del self.vertices[node_id]

    @pyqtSlot(tuple)
    def add_vertex(self, position):
        available_id = max(list(self.vertices.keys())) + 1
        node = Node(available_id, position[0], position[1])
        self.scene.addItem(self.create_vertex(node))


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
        '''
        if edge.directed:
            self.create_arrowhead(line)'''

        # Add the edge to the origin/end vertex's edges list
        origin_vertex.add_connection(line)
        end_vertex.add_connection(line)

        # Return the edge
        return line

    def buttons_handler(self):
        button_type = self.sender().text()
        modes[button_type] = not modes[button_type]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
