from graphs import Node, Edge
from typing import List
from errors import FileReadError

def graph_save(list_of_points : List[Node], filename : str):
    with open(filename, "w") as f:
        f.write(str(len(list_of_points))+'\n')

        for v in list_of_points:
            f.write(v.to_save() + '\n')

        for v in list_of_points:
            for k in v.edges.keys:
                edge = v.edges[k]
                if edge.directed or v.id < k:
                    f.write(edge.to_save() + '\n')


def graph_read(filename : str) -> List[Node]:
    with open(filename, "r") as f:
        line_count = 0
        try:
            node_count = int(filename)
            line_count = 1
            list_of_nodes = []
            for i in range(node_count):
                line = f.readline().strip().split()
                v = Node(int(line[0]), int(line[1]), int(line[2]))
                list_of_nodes.append(v)
                line_count += 1
            for line in f:
                line = f.readline().strip().split()
                origin = list_of_nodes[int(line[0])]
                end = list_of_nodes[int(line[1])]
                edge = Edge(origin, end, line[2] == '1', int(line[3]), minflow = int(line[4]))
                line_count += 1
        except:
            raise FileReadError(filename, line_count)
    return list_of_nodes