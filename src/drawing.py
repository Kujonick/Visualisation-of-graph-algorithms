import os
import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsTextItem, \
    QGraphicsEllipseItem, QGraphicsLineItem, QPushButton, QGridLayout, QDialog, QLabel, QLineEdit, QVBoxLayout, \
    QMessageBox, QRadioButton, QHBoxLayout, QGroupBox, QComboBox, QGraphicsPolygonItem, qApp
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QLineF, pyqtSignal, pyqtSlot, QProcess, QCoreApplication
from typing import List, Dict

from graphs import Node, Edge
from savers import graph_save, graph_read
from errors import FileReadError

from algorythms.algorythmSteps import AlgorythmSteps
from algorythms.Primitive import BFS, DFS  
from algorythms.PathFinders import Dijkstra
modes = {
    "Add Vertex": False,
    "Add Edge": False,
    "Delete Vertex/Edge": False,
    "Run" : False
}

checks = {}

algorythms_names = {
    "Primitive": ["BFS", "DFS"]
}


algorythms = {
    "BFS" : BFS,
    "DFS" : DFS,
    "Dijkstra" : Dijkstra
}

Vertex_Colors = {
    "visited": (182, 182, 182),
    "unvisited": (169, 192, 255),
}

def get_vertex_value():
    dialog = QDialog()
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

    def get_text_value():
        value = value_input.text()

        if not value:
            QMessageBox.warning(dialog, "Warning", "Please enter value for vertex.")
            return
        
        dialog.accept()

    create_button.clicked.connect(get_text_value)
    dialog.exec_()
    return value_input.text()


class Vertex(QGraphicsEllipseItem):
    window = None
    def __init__(self, node: Node):
        super().__init__(node.x, node.y, 34, 34)
        # Remember initial position of vertex for mouseReleaseEvent
        self.initial_x = node.x
        self.initial_y = node.y

        # Set the pen and brush for the vertex
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)
        

        # Make the vertex movable
        self.setFlag(self.ItemIsMovable)
        # Store a reference to the Node object
        self.node: Node = node
        node.vertex = self
        self.changed_state()
        # Store edges of the Vertex
        self.connections = []

        # Text value
        # if checks.get("With Value", False):
        self.value: QGraphicsTextItem = QGraphicsTextItem('-')
        self.value.setDefaultTextColor(QColor(255, 0, 0))
        self.value.setParentItem(self)
        text_rect = self.value.boundingRect()
        self.value.setPos(node.x - text_rect.width() / 2 + 15, node.y - 4 * text_rect.height() / 5 + 17)

        # Set signal in case of removal

    def get_connection(self, other):
        for conn in self.connections:
            if self == conn.origin and other == conn.end:
                return conn
            elif self == conn.end and other == conn.origin:
                return conn
        return None
    
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
            return
        
        if event.button() == Qt.LeftButton and modes["Add Edge"]:
            if self.window.selected is None:
                self.window.select_origin_vertex(self)

            elif self == self.window.selected:
                self.window.unselect_origin_vertex()

            else:
                self.window.add_new_edge(self)
            
        
        if event.button() == Qt.RightButton and checks.get("With Value", False) and not modes["Run"]:
            
            value = get_vertex_value()
            self.node.value = value
            self.changed_value()


            

    def remove(self):
        list_of_conn = self.connections
        for conn in list_of_conn[::-1]:
            conn.remove()

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
            self.change_color(Vertex_Colors["unvisited"])

    def clear_value(self):
        self.value.setPlainText('')

    def changed_value(self):
        self.value.setPlainText(str(self.node.value))

    def set_selected(self):
        pen = QPen(Qt.red)
        pen.setWidth(3)
        self.setPen(pen)

    def set_unselected(self):
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)


class Arrowhead(QGraphicsPolygonItem):
        def __init__(self, connection):
            super().__init__(None)
            self.connection : Connection = connection

            self.setPen(self.connection.pen())
            brush = QBrush(Qt.black)
            self.setBrush(brush)
            self.update_triangle()
        
        def update_triangle(self):
            vector = [self.connection.origin_x - self.connection.end_x, self.connection.origin_y - self.connection.end_y]
            length = (vector[0]**2 + vector[1]**2)**0.5
            if length == 0:
                return
            vector[0], vector[1] = vector[0]/length, vector[1]/length
            pvector = [-vector[1], vector[0]]

            new_traingle = QPolygonF()
            node_r = 17
            h = 10 + node_r # height of arrow
            w = 5           # width of arrow
            new_traingle.append(QPointF(self.connection.end_x + node_r*vector[0], self.connection.end_y + node_r*vector[1]))
            new_traingle.append(QPointF(self.connection.end_x + h*vector[0] + w*pvector[0], self.connection.end_y + h*vector[1] + w*pvector[1]))
            new_traingle.append(QPointF(self.connection.end_x + h*vector[0] - w*pvector[0], self.connection.end_y + h*vector[1] - w*pvector[1]))
            self.setPolygon(new_traingle)


class Connection(QGraphicsLineItem):
    def __init__(self, origin, end, directed, edge):
        
        self.origin_x = origin.initial_x + 17 + origin.x()
        self.origin_y = origin.initial_y + 17 + origin.y()
        self.end_x = end.initial_x + 17 + end.x()
        self.end_y = end.initial_y + 17 + end.y()
        super().__init__(self.origin_x, self.origin_y,
                         self.end_x, self.end_y)
        self.origin: Vertex = origin
        self.end: Vertex = end
        self.directed = directed
        self.arrowhead: Arrowhead = None
        self.edge: Edge = edge
        self.edge.connection = self
        
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)

        if not checks.get("Unweighted", False):
            self.weight_text = QGraphicsTextItem(self)
            if checks.get("Weighted", False):
                self.update_weight()
            else:
                self.uptade_maxflow()

            self.weight_text.setDefaultTextColor(Qt.black)
            # Calculate the position of the weight text
            angle = math.atan2(self.line().dy(), self.line().dx())
            offset = 15
            text_x = self.line().center().x() + offset * math.sin(angle)
            text_y = self.line().center().y() - offset * math.cos(angle)
            self.weight_text.setPos(text_x - self.weight_text.boundingRect().width() / 2,
                                    text_y - self.weight_text.boundingRect().height() / 2)
        if directed:
            self.arrowhead = Arrowhead(self)
            

    def __eq__(self, other):
        if not isinstance(other, Connection):
            return False
        return other.edge == self.edge

    def __hash__(self) -> int:
        return hash(self.edge) * 11

    def __str__(self):
        return f"Conn {str(self.edge)}"

    def add_arrowhead_to_scene(self):
        self.scene().addItem(self.arrowhead)

    def adjust(self):
        self.origin_x = self.origin.initial_x + 17 + self.origin.x()
        self.origin_y = self.origin.initial_y + 17 + self.origin.y()
        self.end_x = self.end.initial_x + 17 + self.end.x()
        self.end_y = self.end.initial_y + 17 + self.end.y()
        start_pos = QPointF(self.origin_x, self.origin_y)
        end_pos = QPointF(self.end_x, self.end_y)
        line = QLineF(start_pos, end_pos)
        self.setLine(line)

        if not checks.get("Unweighted", False):
            # Calculate the position of the weight text
            angle = math.atan2(line.dy(), line.dx())
            offset = 15
            text_x = self.line().center().x() + offset * math.sin(angle)
            text_y = self.line().center().y() - offset * math.cos(angle)
            self.weight_text.setPos(text_x - self.weight_text.boundingRect().width() / 2,
                                    text_y - self.weight_text.boundingRect().height() / 2)

        if self.directed:
            self.arrowhead.update_triangle()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and modes["Delete Vertex/Edge"]:
            self.remove()

            return
        if event.button() == Qt.LeftButton and True not in modes.values() and not checks.get("Unweighted", False):
            def change_button():
                given_value = new_value.text()
                if len(given_value) == 0:
                    QMessageBox.warning(dialog, "Warning",
                                            "Number must be at least one digit ")
                    return 
                if given_value[0] == '0':
                    QMessageBox.warning(dialog, "Warning",
                                            "Number can't start with 0 (especialy be '0')")
                    return 
                for sign in given_value:
                    if sign not in '0123456789':
                        QMessageBox.warning(dialog, "Warning",
                                            "Only numbers [1-9][0-9]*, no floats")
                        return
                    
                if checks.get("Weighted", False):
                    self.edge.set_cost(int(given_value))
                    self.update_weight()
                else:
                    self.edge.set_maxflow(int(given_value))
                    self.uptade_maxflow()
                dialog.close()
                return

            dialog = QDialog(self.window())
            dialog.setWindowTitle("Change edge")
            dialog.setGeometry(300, 300, 300, 100)
            dialog.setModal(True)
            if checks.get("Weighted", False):
                number_label = QLabel("New Edge weight:")
            else:
                number_label = QLabel("New Edge max flow:")

            new_value = QLineEdit()
            confirm_button = QPushButton("Set")

            layout = QVBoxLayout()
            layout.addWidget(number_label)
            layout.addWidget(new_value)

            layout.addWidget(confirm_button)
            confirm_button.clicked.connect(change_button)

            dialog.setLayout(layout)
            dialog.exec_()
            #########################

    def remove(self):
        self.origin.connections.remove(self)
        self.end.connections.remove(self)
        self.edge.remove()
        if self.directed:
            self.scene().removeItem(self.arrowhead)
        self.scene().removeItem(self)
        
        del self

    def set_selected(self):
        pen = QPen(Qt.red)
        pen.setWidth(2)
        self.setPen(pen)

    def set_unselected(self):
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)

    def update_weight(self):
        if self.edge.cost is not None:
            self.weight_text.setPlainText(str(self.edge.cost))
        else:
            self.weight_text.setPlainText("-")

    def uptade_maxflow(self):
        if self.edge.maxflow is not None:
            self.weight_text.setPlainText(f"/ {str(self.edge.maxflow)}")
        else:
            self.weight_text.setPlainText("/-")


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

        # setting up verticies
        Vertex.window = self
        self.selected :Vertex = None

        if checks.get("Weighted", False):
            algorythms_names["PathFinders"] = ["Dijkstra"]

        # OTHER 


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
        self.setWindowTitle("Visualization of graph algorythms")
        self.setGeometry(100, 100, 800, 600)

        # Turning off scrolls on the edges of window
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add the view to the window
        self.setCentralWidget(self.view)
        self.vertices: Dict[int: Vertex] = {}
        self.initialize_graph()
        # Initialize UI #

        # Create grid and buttons
        self.grid = QGridLayout(self.view)

        # Modifycation buttons
        self.delete_mode_button = QPushButton("Delete Vertex/Edge", self)
        self.delete_mode_button.clicked.connect(self.buttons_handler)
        self.add_vertex_mode_button = QPushButton("Add Vertex", self)
        self.add_vertex_mode_button.clicked.connect(self.buttons_handler)
        self.add_edge_mode_button = QPushButton("Add Edge", self)
        self.add_edge_mode_button.clicked.connect(self.buttons_handler)

        # # Algorythm button
        self.algorithm_button = QPushButton("Algorithms...", self)
        self.algorithm_button.clicked.connect(self.run_algorithm)

        # File buttons 
        self.save_graph_button = QPushButton("Save to file", self)
        self.save_graph_button.clicked.connect(self.save_to_file)
        self.load_graph_button = QPushButton("Load to file", self)
        self.load_graph_button.clicked.connect(self.load_from_file)

        # Running algorythm buttons
        self.next_step_button = QPushButton("Next", self)
        self.next_step_button.setEnabled(False)
        # self.algorithm_button.clicked.connect(self.run_algorithm)
        
        self.prev_step_button = QPushButton("Previous", self)
        self.prev_step_button.setEnabled(False)

        self.first_step_button = QPushButton("To Start", self)
        self.first_step_button.setEnabled(False)

        self.last_step_button = QPushButton("To End", self)
        self.last_step_button.setEnabled(False)

        # return button
        self.back_button = QPushButton("Back", self)
        self.back_button.clicked.connect(self.back_button_action)


        self.first_step_button.clicked.connect(lambda : self.run_button_clicked(self.algorythm.to_first))
        self.next_step_button.clicked.connect(lambda : self.run_button_clicked(self.algorythm.next))
        self.prev_step_button.clicked.connect(lambda : self.run_button_clicked(self.algorythm.prev))
        self.last_step_button.clicked.connect(lambda : self.run_button_clicked(self.algorythm.to_last))

        # Editing Modes
        self.previous_mode = None


        # Labels
        add_vertex_mode_label = QLabel(self)
        add_edge_mode_label = QLabel(self)
        delete_mode_label = QLabel(self)
        run_mode_label = QLabel(self)
        add_vertex_mode_label.setText("ADD VERTEX MODE ENABLED")
        add_vertex_mode_label.setVisible(False)
        add_edge_mode_label.setText("ADD EDGE MODE ENABLED")
        add_edge_mode_label.setVisible(False)
        delete_mode_label.setText("DELETE MODE ENABLED")
        delete_mode_label.setVisible(False)
        run_mode_label.setText("RUNNING")
        run_mode_label.setVisible(False)
        self.mode_labels = {
            "Add Vertex": add_vertex_mode_label,
            "Add Edge": add_edge_mode_label,
            "Delete Vertex/Edge": delete_mode_label,
            "Run": run_mode_label 
        }

        # Adding all labels to viev
        self.grid.addWidget(add_vertex_mode_label, 0, 3, Qt.AlignTop | Qt.AlignCenter)
        self.grid.addWidget(add_edge_mode_label, 0, 3, Qt.AlignTop | Qt.AlignCenter)
        self.grid.addWidget(delete_mode_label, 0, 3, Qt.AlignTop | Qt.AlignCenter)
        self.grid.addWidget(run_mode_label, 0, 3, Qt.AlignTop | Qt.AlignCenter)

        # And buttons
        self.grid.addWidget(self.add_vertex_mode_button, 1, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addWidget(self.add_edge_mode_button, 1, 1, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addWidget(self.delete_mode_button, 1, 2, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addWidget(self.algorithm_button, 1, 3, Qt.AlignBottom)
        self.grid.addWidget(self.save_graph_button, 1, 8, Qt.AlignRight | Qt.AlignBottom)
        self.grid.addWidget(self.load_graph_button, 1, 9, Qt.AlignRight | Qt.AlignBottom)
        
        self.grid.addWidget(self.next_step_button, 0, 8, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.grid.addWidget(self.prev_step_button, 0, 7, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.grid.addWidget(self.first_step_button, 0, 6, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.grid.addWidget(self.last_step_button, 0, 9, 1, 1, Qt.AlignTop | Qt.AlignRight)

        self.grid.addWidget(self.back_button, 0, 0, 1, 2, Qt.AlignTop | Qt.AlignLeft)


        self.grid.setColumnStretch(3, 1)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)

    def initialize_graph(self):
        # example nodes
        self.nodes.extend([Node(0, 100, 100), Node(1, 200, 200), Node(2, 300, 100)])
        nodes = [Node(0, 100, 100), Node(1, 200, 200), Node(2, 300, 100)]
        nodes[0].connect(nodes[1], directed=checks.get("Directed", False))
        # nodes[0].connect(nodes[2], False)
        nodes[2].connect(nodes[1], directed=checks.get("Directed", False))

        # Add the nodes to the scene
        for node in nodes:
            vertex = self.create_vertex(node)
            self.vertices[node.id] = vertex
            self.scene.addItem(vertex)
        edges = set()
        for node in nodes:
            for edge in node.edges.values():
                edges.add(edge)
        if checks.get("Directed", False):
            for edge in edges:
                edge.directed = True
        if checks.get("Weighted", False):
            for edge in edges:
                edge.set_cost(1)
        if checks.get("Flow", False):
            for edge in edges:
                edge.set_maxflow(1)
        for edge in edges:
            connection: Connection = self.create_edge(edge)
            self.scene.addItem(connection)
            if checks.get("Directed", False):
                connection.add_arrowhead_to_scene()
            # line = self.create_edge(edge)
            # self.scene.addItem(line)
            # if checks.get("Directed", False):
            #     line.add_arrowhead_to_scene()
        for v in self.vertices.values():
            v.show()

    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key_Left:
            # Obsługa ruchu w lewo
            self.move(self.x() - 10, self.y())
        elif key == Qt.Key_Right:
            # Obsługa ruchu w prawo
            self.move(self.x() + 10, self.y())
        elif key == Qt.Key_Up:
            # Obsługa ruchu w górę
            self.move(self.x(), self.y() - 10)
        elif key == Qt.Key_Down:
            # Obsługa ruchu w dół
            self.move(self.x(), self.y() + 10)

    # sets modification buttons on and off
    def set_edit_buttons(self, edit_mode : bool): 
        '''
        sets Editing, loading and algorythm buttons 'Enabled' status to [edit_mode]
        '''
        self.delete_mode_button.setEnabled(edit_mode)
        self.add_edge_mode_button.setEnabled(edit_mode)
        self.add_vertex_mode_button.setEnabled(edit_mode)
        self.save_graph_button.setEnabled(edit_mode)
        self.load_graph_button.setEnabled(edit_mode)
        self.algorithm_button.setEnabled(edit_mode)

    def update_run_buttons(self, run_mode=True):
        self.last_step_button.setEnabled(self.algorythm.check_next()& run_mode)
        self.next_step_button.setEnabled(self.algorythm.check_next()& run_mode)
        self.first_step_button.setEnabled(self.algorythm.check_prev()& run_mode)
        self.prev_step_button.setEnabled(self.algorythm.check_prev()& run_mode)
    
    def run_button_clicked(self, function):
        function()
        self.update_run_buttons()

    def set_run_buttons(self, run_mode : bool):
        '''
        sets steps settings buttons 'Enabled' status to [run_mode]
        '''
        self.update_run_buttons(run_mode)


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
        # if checks.get("With Value", False):
        text.setPos(node.x - text_rect.width() / 2 + 17, node.y - text_rect.height() / 4 + 17)
        # else:
        #     text.setPos(node.x - text_rect.width() / 2 + 17, node.y - text_rect.height() / 2 + 17)

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
            value = self.get_vertex_value()
            node.change_value(value)
        vertex = self.create_vertex(node)
        self.vertices[node.id] = vertex
        self.scene.addItem(vertex)

    def create_connection(self, edge):
        # Create an edge to represent the connection between two vertices
        origin_vertex = self.vertices[edge.origin.id]
        end_vertex = self.vertices[edge.end.id]
        line = Connection(origin_vertex, end_vertex, edge.directed, edge)

        # text_rect = text.boundingRect()
        # Set the pen for the edge
        # moved to __init__

        # Add the edge to the origin/end vertex's edges list
        origin_vertex.add_connection(line)
        end_vertex.add_connection(line)
        self.scene.addItem(line)

        if checks.get("Directed", False):
            line.add_arrowhead_to_scene()
        # Return the connection
        return line

    def select_origin_vertex(self, vertex:Vertex):
        self.selected = vertex
        vertex.set_selected()

    def unselect_origin_vertex(self):
        if self.selected is not None:
            self.selected.set_unselected()
            self.selected = None


    def add_new_edge(self, vertex):
        origin : Vertex = self.selected
        end : Vertex = vertex
        if origin == end:
            QMessageBox.warning(None, "Warning", "Program does not support multigraphs - loops are not allowed.")
            return

        # check if there is already an edge between the vertices
        if origin.node.get_edge(end.node.id):
            QMessageBox.warning(None, "Warning", "There is already an edge between these vertices.\
            Program does not support multigraphs.")
            return

        if not checks.get("Unweighted", False):

            def check_value():
                value = value_input.text()
                if not value:
                    QMessageBox.warning(dialog, "Warning", "Please enter the weight of the edge.")

                if len(value) == 0:
                    QMessageBox.warning(dialog, "Warning",
                                            "Number must be at least one digit ")
                    return 
                if value[0] == '0':
                    QMessageBox.warning(dialog, "Warning",
                                            "Number can't start with 0 (especialy be '0')")
                    return 
                for sign in value:
                    if sign not in '0123456789':
                        QMessageBox.warning(dialog, "Warning",
                                            "Only numbers [1-9][0-9]*, no floats")
                        return
                dialog.accept()
                    
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Edge")
            dialog.setGeometry(300, 300, 300, 100)
            dialog.setModal(True)

            layout = QVBoxLayout()

            if checks.get("Weighted", False):
                value_label = QLabel("Weight:")
            else:
                value_label = QLabel("Maxflow:")
            value_input = QLineEdit()
            layout.addWidget(value_label)
            layout.addWidget(value_input)

            connect_button = QPushButton("Connect")
            layout.addWidget(connect_button)
            dialog.setLayout(layout)
            connect_button.clicked.connect(check_value)
            exit = dialog.exec_()
            if exit != QDialog.Accepted:
                return 

            directed = checks.get("Directed", False)

            if checks.get("Weighted", False):
                origin.node.connect(end.node, directed, cost = int(value_input.text()))
            elif checks.get("Flow", False):
                origin.node.connect(end.node, directed, maxflow = int(value_input.text()))
        else:
            origin.node.connect(end.node, checks.get("Directed", False))
        self.create_connection(origin.node.get_edge(end.node.id))
        self.unselect_origin_vertex()

    def turn_off_modes(self):
        for mode in modes:
            modes[mode] = False
        if self.previous_mode is not None:
            self.mode_labels[self.previous_mode].setVisible(False)

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
            print(checks)
            dialog.accept()

        create_button.clicked.connect(create_graph)

        checklists_layout.addWidget(checklist_direction_group_box)
        checklists_layout.addWidget(checklist_edges_group_box)
        checklists_layout.addWidget(checklist_nodes_group_box)
        layout.addLayout(checklists_layout)
        layout.addWidget(create_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def back_button_action(self):
        if modes["Run"]:
            self.turn_edit_mode()
        else:
            self.vertices.clear()
            self.nodes.clear()
            self.scene.clear()
            checks.clear()
            self.starting_window()
            self.initialize_graph()



    def turn_run_mode(self, dialog_window, algo_name):####


        self.algorythm : BFS= algorythms[algo_name](self.vertices)
        def acceptence():
            text = input.text()
            if len(text) == 0:
                QMessageBox.warning(param_dialog, "Warning",
                                        "Empty input")
                return
            for sign in text:
                if sign not in '0123456789':
                    QMessageBox.warning(param_dialog, "Warning",
                                        "Use only numbers")
                    return
            if self.algorythm.constrains(params[i], int(text)):
                self.algorythm.set_parameters(params[i], int(text))
                param_dialog.accept()
            else:
                QMessageBox.warning(param_dialog, "Warning",
                                        "Wrong parameter value")

        # taking parameters needed for algorythm to start
        i = 0
        params = self.algorythm.get_parameters_name()
        while i < len(params):
            param_dialog = QDialog(self)
            param_dialog.setWindowTitle("Insert value of parameter")
            param_dialog.setGeometry(300, 300, 300, 100)
            param_dialog.setModal(True)

            layout = QVBoxLayout()
            accept_button = QPushButton("Accept")
            label = QLabel(params[i])
            input = QLineEdit()

            layout.addWidget(label)
            layout.addWidget(input)
            layout.addWidget(accept_button)

            accept_button.clicked.connect(acceptence)

            param_dialog.setLayout(layout)
            exit_value = param_dialog.exec_()
            if exit_value != QDialog.Accepted:
                self.algorythm = None
                return 
            i += 1

        # seting up
        
        self.set_edit_buttons(False)
        self.turn_off_modes()
        self.previous_mode = "Run"
        modes["Run"] = True
        for vert in self.vertices.values():
            vert.node.change_visited(False)
        self.mode_labels["Run"].setVisible(True)
        self.algorythm.start()
        self.set_run_buttons(True)
        dialog_window.accept()

    def turn_edit_mode(self):
        self.set_run_buttons(False)
        self.algorythm.to_first()
        modes["Run"] = False
        self.algorythm = None
        self.mode_labels["Run"].setVisible(False)
        self.set_edit_buttons(True)
        

    def run_algorithm(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Run Algorithm")
        dialog.setGeometry(300, 300, 300, 100)
        dialog.setModal(True)

        layout = QVBoxLayout()

        # Create the first dropdown list
        category_combo = QComboBox()
        category_combo.addItem("Type of algorithm")
        for name in algorythms_names:
            category_combo.addItem(name)

        layout.addWidget(category_combo)

        algorithm_combo = QComboBox()
        layout.addWidget(algorithm_combo)

        run_button = QPushButton("Run")
        layout.addWidget(run_button)
        run_button.setEnabled(False)

        def update_algorithms():
            category = category_combo.currentText()
            algorithm_combo.clear()
            run_button.setEnabled(True)
            algorithm_combo.addItems(algorythms_names[category])

        category_combo.currentIndexChanged.connect(update_algorithms)


        run_button.clicked.connect(lambda : self.turn_run_mode(dialog, algorithm_combo.currentText())) # lambda because it must be function
        # Create the second dropdown list
        dialog.setLayout(layout)
        dialog.exec_()


    
    def get_extension(self):
        def complete_enxtenstion(check, present, other):
            if checks.get(check, False):
                extension.append(present)
            else:
                extension.append(other)

        extension = []
        complete_enxtenstion('Undirected','u','d')
        complete_enxtenstion('Unweighted','u','w')
        complete_enxtenstion('No Value','n','v')
        return '.'+''.join(extension)
    # Saves .nodes to file named by user
    def save_to_file(self):

        def saving_button():
            filename = filename_input.text()
            for sign in '.#%&*{/\\}?:@:"\'!`|=+<>':
                if sign in filename:
                    QMessageBox.warning(dialog, "Warning",
                                        "Wrong filename, use only letters, numbers, signs like '_-,'")
                    return
            
            
            form = self.get_extension()
            graph_save([v.node for v in self.vertices.values()], filename+form)
            dialog.close()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Saving to file")
        dialog.setGeometry(300, 300, 300, 100)
        dialog.setModal(True)

        filename_label = QLabel("Filename (dont use formats):")
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
            for sign in '#%&*{/\\}?:@.:"\'!`|=+<>':
                if sign in filename:
                    QMessageBox.warning(dialog, "Warning",
                                        "Wrong filename, use only letters, numbers, signs like '_-,'")
                    return
            try:
                form = self.get_extension()
                nodes: list[Node] = graph_read(filename+form)
                vertices: list[Vertex] = [x for x in self.vertices.values()]
                for x in vertices:
                    x.remove()
                self.vertices.clear()
                for node in nodes:
                    self.scene.addItem(self.create_vertex(node))
                    node.show()
                for node in nodes:
                    for edge in node.edges.values():
                        if node != edge.origin:
                            continue
                        line = self.create_connection(edge)

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

        filename_label = QLabel("Filename (don't write format): ")
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
