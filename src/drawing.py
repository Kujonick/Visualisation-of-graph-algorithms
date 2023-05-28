import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsTextItem, \
    QGraphicsEllipseItem, QGraphicsLineItem, QPushButton, QGridLayout, QDialog, QLabel, QLineEdit, QVBoxLayout, \
    QMessageBox, QRadioButton, QHBoxLayout, QGroupBox, QComboBox
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QLineF, pyqtSignal, pyqtSlot
from typing import List, Dict

from graphs import Node, Edge
from savers import graph_save, graph_read
from errors import FileReadError

modes = {
    "Add Vertex": False,
    "Delete Vertex/Edge": False
}

checks = {}

algorithms = {
    "1": ["algo1", "algo2", "algo3"],
    "2": ["algo4", "algo5", "algo6"],
    "3": ["algo7", "algo8", "algo9"]
}

Vertex_Colors = {
    "visited": (182, 182, 182),
    "unvisited": (169, 192, 255),
}


class Vertex(QGraphicsEllipseItem):
    def __init__(self, node: Node):
        super().__init__(node.x, node.y, 34, 34)
        # Remember initial position of vertex for mouseReleaseEvent
        self.initial_x = node.x
        self.initial_y = node.y

        # Set the pen and brush for the vertex
        pen = QPen(Qt.black)
        pen.setWidth(2)
        brush = QBrush(QColor(194, 223, 255))
        self.setPen(pen)
        self.setBrush(brush)

        # Make the vertex movable
        self.setFlag(self.ItemIsMovable)
        # Store a reference to the Node object
        self.node: Node = node
        node.vertex = self

        # Store edges of the Vertex
        self.connections = []

        # Text value
        if checks.get("With Value", False):
            self.value: QGraphicsTextItem = QGraphicsTextItem('-')
            self.value.setDefaultTextColor(QColor(255, 0, 0))
            self.value.setParentItem(self)
            text_rect = self.value.boundingRect()
            self.value.setPos(node.x - text_rect.width() / 2 + 15, node.y - 4 * text_rect.height() / 5 + 17)

        # Set signal in case of removal

    def __eq__(self, other):
        if not isinstance(other, Vertex):
            return False
        return self.node == other.node

    def __hash__(self) -> int:
        return hash(self.node) * 13

    def __str__(self):
        return f"Vert {str(self.node)}"

    def show(self):
        for conn in self.connections:
            print(conn)
        print(self)

    def add_connection(self, edge):
        self.connections.append(edge)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        for edge in self.connections:
            edge.adjust()

        self.node.update_position(self.initial_x + self.x(), self.initial_y + self.y())

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and modes["Delete Vertex/Edge"]:
            self.remove()

    def remove(self):
        for edge in self.connections[::-1]:
            edge.remove()

        self.connections.clear()
        self.scene().vertex_deleted_sig.emit(self.node.id)
        self.scene().removeItem(self)
        del self

    def change_color(self, colors: tuple):
        new_brush = QBrush(QColor(colors[0], colors[1], colors[2]))
        self.setBrush(new_brush)

    def changed_state(self):
        if self.node.visited:
            self.change_color(Vertex_Colors["visited"])
        else:
            self.change_color(Vertex_Colors("unvisited"))

    def clear_value(self):
        self.value.setPlainText('')

    def changed_value(self):
        self.value.setPlainText(str(self.node.value))

    def set_selected(self):
        pen = QPen(Qt.red)
        pen.setWidth(5)
        self.setPen(pen)

    def set_unselected(self):
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)


class Connection(QGraphicsLineItem):
    def __init__(self, origin, end, directed, edge):
        super().__init__(origin.initial_x + 17 + origin.x(), origin.initial_y + 17 + origin.y(),
                         end.initial_x + 17 + end.x(), end.initial_y + 17 + end.y())
        self.origin: Vertex = origin
        self.end: Vertex = end
        self.directed = directed
        self.arrowhead = None
        self.edge: Edge = edge
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)

        if checks.get("Weighted", False):
            self.weight_text = QGraphicsTextItem(self)
            if self.edge is not None and self.edge.cost is not None:
                self.weight_text.setPlainText(str(self.edge.cost))
            else:
                self.weight_text.setPlainText("1")
            self.weight_text.setDefaultTextColor(Qt.black)
            # Calculate the position of the weight text
            angle = math.atan2(self.line().dy(), self.line().dx())
            offset = 15
            text_x = self.line().center().x() + offset * math.sin(angle)
            text_y = self.line().center().y() - offset * math.cos(angle)
            self.weight_text.setPos(text_x - self.weight_text.boundingRect().width() / 2,
                                    text_y - self.weight_text.boundingRect().height() / 2)

    def __eq__(self, other):
        if not isinstance(other, Connection):
            return False
        return other.edge == self.edge

    def __hash__(self) -> int:
        return hash(self.edge) * 11

    def __str__(self):
        return f"Conn {str(self.edge)}"

    def adjust(self):
        start_pos = QPointF(self.origin.initial_x + self.origin.x() + 17, self.origin.initial_y + self.origin.y() + 17)
        end_pos = QPointF(self.end.initial_x + self.end.x() + 17, self.end.initial_y + self.end.y() + 17)
        line = QLineF(start_pos, end_pos)
        self.setLine(line)

        if checks.get("Weighted", False):
            # Calculate the position of the weight text
            angle = math.atan2(line.dy(), line.dx())
            offset = 15
            text_x = self.line().center().x() + offset * math.sin(angle)
            text_y = self.line().center().y() - offset * math.cos(angle)
            self.weight_text.setPos(text_x - self.weight_text.boundingRect().width() / 2,
                                    text_y - self.weight_text.boundingRect().height() / 2)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and modes["Delete Vertex/Edge"]:
            # self.origin.connections.remove(self)
            # self.end.connections.remove(self)
            self.remove()

    def remove(self):
        self.origin.connections.remove(self)
        self.end.connections.remove(self)
        self.edge.remove()
        self.scene().removeItem(self)
        del self

    def set_selected(self):
        pen = QPen(Qt.red)
        self.setPen(pen)

    def set_unselected(self):
        pen = QPen(Qt.black)
        self.setPen(pen)


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

        # Run Starting Window
        self.starting_window()
        if not checks:
            sys.exit()

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
        self.vertices: Dict[int: Vertex] = {}

        # Add the nodes to the scene
        for node in nodes:
            vertex = self.create_vertex(node)
            self.vertices[node.id] = vertex
            self.scene.addItem(vertex)
        edges = set()
        for node in nodes:
            for edge in node.edges.values():
                edges.add(edge)
        for edge in edges:
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

        self.algorithm_button = QPushButton("Algorithms...", self)
        self.algorithm_button.clicked.connect(self.run_algorithm)

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
        self.grid.addWidget(self.algorithm_button, 1, 3, Qt.AlignBottom)
        self.grid.addWidget(self.save_graph_button, 1, 8, Qt.AlignRight | Qt.AlignBottom)
        self.grid.addWidget(self.load_graph_button, 1, 9, Qt.AlignRight | Qt.AlignBottom)

        self.grid.setColumnStretch(3, 1)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

    def create_vertex(self, node: Node):
        # Create a QGraphicsTextItem to hold the node index
        text = QGraphicsTextItem(str(node.id))
        # Create a vertex to represent the node
        vertex = Vertex(node)
        if node.value is not None:
            vertex.changed_value()
        # vertex.deleted.connect(self.delete_vertex)

        # Add the text to the vertex
        text.setParentItem(vertex)
        text_rect = text.boundingRect()
        if checks.get("With Value", False):
            text.setPos(node.x - text_rect.width() / 2 + 17, node.y - text_rect.height() / 4 + 17)
        else:
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
        available_id = max(list(self.vertices.keys())) + 1 if len(self.vertices) > 0 else 0
        node = Node(available_id, position[0], position[1])
        if checks.get("With Value", False):
            dialog = QDialog(self)
            dialog.setWindowTitle("Set vertex value")
            dialog.setGeometry(300, 300, 300, 100)
            dialog.setModal(True)

            value_label = QLabel("Value:")
            value_input = QLineEdit()

            create_button = QPushButton("Create Vertex")

            # layout for the dialog window
            layout = QVBoxLayout()
            layout.addWidget(value_label)
            layout.addWidget(value_input)
            layout.addWidget(create_button)
            dialog.setLayout(layout)

            def set_vertex_value():
                value = value_input.text()

                if not value:
                    QMessageBox.warning(dialog, "Warning", "Please enter value for vertex.")
                    return

                node.change_value(value)
                dialog.accept()

            create_button.clicked.connect(set_vertex_value)
            dialog.exec_()

        vertex = self.create_vertex(node)
        self.vertices[node.id] = vertex
        self.scene.addItem(vertex)

    def create_edge(self, edge):
        # Create an edge to represent the connection between two vertices
        origin_vertex = self.vertices[edge.origin.id]
        end_vertex = self.vertices[edge.end.id]
        line = Connection(origin_vertex, end_vertex, edge.directed, edge)

        # text_rect = text.boundingRect()
        # Set the pen for the edge
        # moved to __init__

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
        weight_label = QLabel("Weight:")
        weight_input = QLineEdit()

        # create button to connect vertices
        connect_button = QPushButton("Connect")

        # layout for the dialog window
        layout = QVBoxLayout()
        layout.addWidget(origin_label)
        layout.addWidget(origin_input)
        layout.addWidget(end_label)
        layout.addWidget(end_input)
        if checks.get("Weighted", False):
            layout.addWidget(weight_label)
            layout.addWidget(weight_input)

        layout.addWidget(connect_button)
        dialog.setLayout(layout)

        def connect_vertices():
            # get the origin and end vertices from the input fields
            origin_id = origin_input.text()
            end_id = end_input.text()
            weight = weight_input.text()

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

            origin: Vertex = self.vertices[origin_id]
            end: Vertex = self.vertices[end_id]

            # check if origin is the same vertex as end
            if origin == end:
                QMessageBox.warning(dialog, "Warning", "Program does not support multigraphs - loops are not allowed.")
                return

            # check if there is already an edge between the vertices
            for edge in origin.connections:
                if edge.end == end:
                    QMessageBox.warning(dialog, "Warning", "There is already an edge between these vertices.\
                    Program does not support multigraphs.")
                    return

            if checks.get("Weighted", False) and not weight:
                QMessageBox.warning(dialog, "Warning", "Please enter the weight of the edge.")
                return

            # connecting nodes
            if checks.get("Weighted", False):
                origin.node.connect(end.node, False, None, None, int(weight))
            else:
                origin.node.connect(end.node, False)

            # create the edge
            edge = origin.node.get_edge(end.node)

            self.scene.addItem(self.create_edge(edge))
            # # Set the pen for the edge
            # pen = QPen(Qt.black)
            # pen.setWidth(2)
            # edge.setPen(pen)

            # # Add edge to the scene and update edges lists in origin and end
            # self.scene.addItem(edge)
            # origin.add_connection(edge)
            # end.add_connection(edge)

            # close the dialog window
            dialog.accept()

        # Connect the button
        connect_button.clicked.connect(connect_vertices)

        # Show
        dialog.exec_()

    def starting_window(self):
        # create a new dialog window
        edge_options = ["Unweighted", "Weighted", "Flow"]
        node_options = ["No Value", "With Value"]
        direction_options = ["Undirected", "Directed"]

        edge_options_checklist = []
        node_options_checklist = []
        direction_options_checklist = []

        dialog = QDialog(self)
        dialog.setWindowTitle("Create new graph")
        dialog.setGeometry(300, 300, 300, 100)
        dialog.setModal(True)

        layout = QVBoxLayout()
        checklists_layout = QHBoxLayout()

        checklist_direction_group_box = QGroupBox()
        checklist_direction_layout = QVBoxLayout()
        checklist_direction_layout.addWidget(QLabel("Direction"))
        first = True
        for option in direction_options:
            radio_button = QRadioButton(option)
            if first:
                radio_button.setChecked(True)
                first = False
            checklist_direction_layout.addWidget(radio_button)
            direction_options_checklist.append(radio_button)
        checklist_direction_group_box.setLayout(checklist_direction_layout)

        checklist_edges_group_box = QGroupBox()
        checklist_edges_layout = QVBoxLayout()
        checklist_edges_layout.addWidget(QLabel("Edges Weights"))
        first = True
        for option in edge_options:
            radio_button = QRadioButton(option)
            if first:
                radio_button.setChecked(True)
                first = False
            checklist_edges_layout.addWidget(radio_button)
            edge_options_checklist.append(radio_button)
        checklist_edges_group_box.setLayout(checklist_edges_layout)

        checklist_nodes_group_box = QGroupBox()
        checklist_nodes_layout = QVBoxLayout()
        checklist_nodes_layout.addWidget(QLabel("Nodes Values"))
        first = True
        for option in node_options:
            radio_button = QRadioButton(option)
            if first:
                radio_button.setChecked(True)
                first = False
            checklist_nodes_layout.addWidget(radio_button)
            node_options_checklist.append(radio_button)
        checklist_nodes_group_box.setLayout(checklist_nodes_layout)

        create_button = QPushButton("Create Graph")

        def create_graph():
            for check in direction_options_checklist:
                if check.isChecked():
                    checks[check.text()] = True
            for check in edge_options_checklist:
                if check.isChecked():
                    checks[check.text()] = True
            for check in node_options_checklist:
                if check.isChecked():
                    checks[check.text()] = True

            dialog.accept()

        create_button.clicked.connect(create_graph)

        checklists_layout.addWidget(checklist_direction_group_box)
        checklists_layout.addWidget(checklist_edges_group_box)
        checklists_layout.addWidget(checklist_nodes_group_box)
        layout.addLayout(checklists_layout)
        layout.addWidget(create_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def run_algorithm(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Run Algorithm")
        dialog.setGeometry(300, 300, 300, 100)
        dialog.setModal(True)

        layout = QVBoxLayout()

        # Create the first dropdown list
        category_combo = QComboBox()
        category_combo.addItem("Type of algorithm")
        category_combo.addItem("1")
        category_combo.addItem("2")
        category_combo.addItem("3")

        layout.addWidget(category_combo)

        algorithm_combo = QComboBox()
        layout.addWidget(algorithm_combo)

        run_button = QPushButton("Run")
        layout.addWidget(run_button)

        def update_algorithms():
            category = category_combo.currentText()
            algorithm_combo.clear()
            algorithm_combo.addItems(algorithms[category])

        category_combo.currentIndexChanged.connect(update_algorithms)

        def run():
            '''
            ######
            '''
            dialog.accept()

        run_button.clicked.connect(run)
        # Create the second dropdown list
        dialog.setLayout(layout)
        dialog.exec_()

    # Saves .nodes to file named by user
    def save_to_file(self):

        def saving_button():
            filename = filename_input.text()
            for sign in '#%&*{/\\}?:@:"\'!`|=+<>':
                if sign in filename:
                    QMessageBox.warning(dialog, "Warning",
                                        "Wrong filename, use only letters, numbers, signs like '_-,.'")
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
                    QMessageBox.warning(dialog, "Warning",
                                        "Wrong filename, use only letters, numbers, signs like '_-,.'")
                    return
            try:
                nodes: list[Node] = graph_read(filename)
                vertices: list[Vertex] = [x for x in self.vertices.values()]
                for x in vertices:
                    x.remove()
                self.vertices.clear()
                for node in nodes:
                    self.scene.addItem(self.create_vertex(node))
                for node in nodes:
                    for edge in node.edges.values():
                        if edge.directed and node != edge.origin:
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
