import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsTextItem, \
    QGraphicsEllipseItem, QGraphicsLineItem, QPushButton, QGridLayout, QDialog, QLabel, QLineEdit, QVBoxLayout, \
    QMessageBox
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, QLineF, pyqtSignal, pyqtSlot
from typing import List, Dict

from graphs import Node
from savers import graph_save, graph_read
from errors import FileReadError
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

    def change_color(self, colors : tuple):
        new_brush = QBrush(QColor(colors[0], colors[1], colors[2]))
        self.setBrush(new_brush)

class Connection(QGraphicsLineItem):
    def __init__(self, origin, end, directed):
        super().__init__(origin.initial_x + 17 + origin.x(), origin.initial_y + 17+ origin.y(), end.initial_x + 17+ end.x(), end.initial_y + 17+ end.y())
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

        # main list of all nodes
        self.nodes: List[Node] = []
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
        self.nodes.extend([Node(0, 100, 100), Node(1, 200, 200), Node(2, 300, 100)])
        nodes = [Node(0, 100, 100), Node(1, 200, 200), Node(2, 300, 100)]
        nodes[0].connect(nodes[1], False)
        # nodes[0].connect(nodes[2], False)
        nodes[2].connect(nodes[1], False)

        # Create a dictionary to store vertex objects
        self.vertices : Dict[int : Vertex] = {}

        # Add the nodes to the scene
        for node in nodes:
            vertex = self.create_vertex(node)
            self.scene.addItem(vertex)
        for node in nodes:
            for edge in node.edges.values():
                self.scene.addItem(self.create_edge(edge))

        # Initialize UI #

        # Create grid and buttons
        self.grid = QGridLayout(self.view)

        self.delete_mode_button = QPushButton("Delete Vertex/Edge", self)
        self.delete_mode_button.clicked.connect(self.buttons_handler)
        self.add_vertex_mode_button = QPushButton("Add Vertex", self)
        self.add_vertex_mode_button.clicked.connect(self.buttons_handler)
        self.add_edge_mode_button = QPushButton("Add Edge", self)
        self.add_edge_mode_button.clicked.connect(self.add_edge)

        self.save_graph_button = QPushButton("Save to file", self)
        self.save_graph_button.clicked.connect(self.save_to_file)
        self.load_graph_button = QPushButton("Load to file", self)
        self.load_graph_button.clicked.connect(self.load_from_file)

        self.previous_mode = None

        add_edge_mode_label = QLabel(self)
        delete_mode_label = QLabel(self)
        add_edge_mode_label.setText("ADD VERTEX MODE ENABLED")
        add_edge_mode_label.setVisible(False)
        delete_mode_label.setText("DELETE MODE ENABLED")
        delete_mode_label.setVisible(False)
        self.mode_labels = {
            "Add Vertex": add_edge_mode_label,
            "Delete Vertex/Edge": delete_mode_label
        }

        self.grid.addWidget(add_edge_mode_label, 0, 0, 1, 2, Qt.AlignLeft | Qt.AlignTop)
        self.grid.addWidget(delete_mode_label, 0, 0, 1, 2, Qt.AlignLeft | Qt.AlignTop)
        self.grid.addWidget(self.add_vertex_mode_button, 1, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addWidget(self.add_edge_mode_button, 1, 1, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addWidget(self.delete_mode_button, 1, 2, Qt.AlignLeft | Qt.AlignBottom)

        self.grid.addWidget(self.save_graph_button, 1, 8, Qt.AlignRight | Qt.AlignBottom)
        self.grid.addWidget(self.load_graph_button, 1, 9, Qt.AlignRight | Qt.AlignBottom)


        self.grid.setColumnStretch(3, 1)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

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
        vertex = self.create_vertex(node)
        self.vertices[node.id] = vertex
        self.scene.addItem(vertex)

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

    def add_edge(self):
        if self.previous_mode is not None:
            modes[self.previous_mode] = False
            self.mode_labels[self.previous_mode].setVisible(False)

        # create a new dialog window
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Edge")
        dialog.setGeometry(300, 300, 300, 100)
        dialog.setModal(True)

        # create labels and text inputs for origin and end vertices
        origin_label = QLabel("Origin:")
        origin_input = QLineEdit()
        end_label = QLabel("End:")
        end_input = QLineEdit()

        # create button to connect vertices
        connect_button = QPushButton("Connect")

        # layout for the dialog window
        layout = QVBoxLayout()
        layout.addWidget(origin_label)
        layout.addWidget(origin_input)
        layout.addWidget(end_label)
        layout.addWidget(end_input)
        layout.addWidget(connect_button)
        dialog.setLayout(layout)

        def connect_vertices():
            # get the origin and end vertices from the input fields
            origin_id = origin_input.text()
            end_id = end_input.text()

            # check if the input fields are not empty
            if not origin_id or not end_id:
                QMessageBox.warning(dialog, "Warning", "Please enter values for both origin and end vertices.")
                return

            origin_id = int(origin_id)
            end_id = int(end_id)

            # check if the origin and end vertices exist in the graph
            if self.vertices.get(origin_id, -1) == -1 or self.vertices.get(end_id, -1) == -1:
                QMessageBox.warning(dialog, "Warning", "One or both of the vertices do not exist in the graph.")
                return

            origin = self.vertices[origin_id]
            end = self.vertices[end_id]

            # check if origin is the same vertex as end
            if origin == end:
                QMessageBox.warning(dialog, "Warning", "Program does not support multigraphs - loops are not allowed.")
                return

            # check if there is already an edge between the vertices
            for edge in origin.edges:
                if edge.end == end:
                    QMessageBox.warning(dialog, "Warning", "There is already an edge between these vertices.\
                    Program does not support multigraphs")
                    return

            # create the edge
            edge = Connection(origin, end, False)

            # Set the pen for the edge
            pen = QPen(Qt.black)
            pen.setWidth(2)
            edge.setPen(pen)

            # Add edge to the scene and update edges lists in origin and end
            self.scene.addItem(edge)
            origin.add_connection(edge)
            end.add_connection(edge)

            # connecting nodes
            origin.node.connect(end.node, True)
            # close the dialog window
            dialog.accept()

        # Connect the button
        connect_button.clicked.connect(connect_vertices)

        # Show
        dialog.exec_()
    
    # Saves .nodes to file named by user
    def save_to_file(self):

        def saving_button():
            filename = filename_input.text()
            for sign in '#%&*{/\\}?:@:"\'!`|=+<>':
                if sign in filename:
                    QMessageBox.warning(dialog, "Warning", "Wrong filename, use only letters, numbers, signs like '_-,.'")
                    return
            graph_save([v.node for v in self.vertices.values()], filename)
            dialog.close()
            return
                
        dialog = QDialog(self)
        dialog.setWindowTitle("Saving to file")
        dialog.setGeometry(300, 300, 300, 100)
        dialog.setModal(True)

        filename_label = QLabel("Filename (recomended .txt):")
        filename_input = QLineEdit()
        confirm_button = QPushButton("Save")

        layout = QVBoxLayout()
        layout.addWidget(filename_label)
        layout.addWidget(filename_input)

        layout.addWidget(confirm_button)
        confirm_button.clicked.connect(saving_button)

        dialog.setLayout(layout)
        dialog.exec_()

    # Loads .nodes from file given by user
    def load_from_file(self):

        def loading_button():
            filename = filename_input.text()
            for sign in '#%&*{/\\}?:@:"\'!`|=+<>':
                if sign in filename:
                    QMessageBox.warning(dialog, "Warning", "Wrong filename, use only letters, numbers, signs like '_-,.'")
                    return
            try: 
                nodes : list[Node] = graph_read(filename)
                vertices : list[Vertex] = [x for x in self.vertices.values()]
                for x in vertices:
                    for edge in x.edges:
                        self.scene.removeItem(edge)
                    self.scene.removeItem(x)
                    self.delete_vertex(x.node.id)
                self.vertices = {}
                for n in nodes:
                    vertex = self.create_vertex(n)
                    self.vertices[n.id] = vertex
                    self.scene.addItem(vertex)
                for node in nodes:
                    for edge in node.edges.values():
                        if not edge.directed and node != edge.origin:
                            continue
                        self.scene.addItem(self.create_edge(edge))

            except FileReadError as e:
                QMessageBox.warning(dialog, f"Error {e.__class__.__name__}", str(e))
                return
            except FileNotFoundError as e:
                QMessageBox.warning(dialog, f"Error {e.__class__.__name__}", str(e))
                return
            dialog.close()
            return
                
        dialog = QDialog(self)
        dialog.setWindowTitle("Loading from file")
        dialog.setGeometry(300, 300, 300, 100)
        dialog.setModal(True)

        filename_label = QLabel("Filename: ")
        filename_input = QLineEdit()
        confirm_button = QPushButton("Load")

        layout = QVBoxLayout()
        layout.addWidget(filename_label)
        layout.addWidget(filename_input)

        layout.addWidget(confirm_button)
        confirm_button.clicked.connect(loading_button)

        dialog.setLayout(layout)
        dialog.exec_()


    def buttons_handler(self):
        button_type = self.sender().text()
        if button_type == self.previous_mode:
            modes[button_type] = not modes[button_type]
            self.mode_labels[button_type].setVisible(not self.mode_labels[button_type].isVisible())
        else:
            if self.previous_mode is not None:
                modes[self.previous_mode] = False
                self.mode_labels[self.previous_mode].setVisible(False)
            self.previous_mode = button_type
            modes[button_type] = True
            self.mode_labels[button_type].setVisible(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
