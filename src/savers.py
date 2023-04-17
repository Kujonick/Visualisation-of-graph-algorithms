from graphs import Node, Edge
from typing import List
from errors import FileReadError

#  saves graph to .txt file
#  structure:
#   "[V]        - amount of Nodes
#    [id x y]   - nodes atributes
#    ...
#    [origin.id end.id directed maxflow minflow cost] - all Edges atributes
#    ...

def graph_save(list_of_points : List[Node], filename : str):
    with open("src/saved_graphs/" + filename, "w") as f:
        f.write(str(len(list_of_points))+'\n')

        for v in list_of_points:
            f.write(v.to_save() + '\n')

        for v in list_of_points:
            for k in v.edges.keys():
                edge : Edge= v.edges[k]
                if edge.directed or v.id < k:
                    f.write(edge.to_save() + '\n')

def txt2int(text : str) :
    if text == 'None':
        return None
    else:
        return int(text)

def graph_read(filename : str) -> List[Node]:
    with open("src/saved_graphs/" + filename, "r") as f:
        line_count = 0
        try:
            node_count = int(f.readline().strip())
            line_count = 1
            list_of_nodes : List[Node]= []
            for i in range(node_count):
                line = f.readline().strip().split()
                v = Node(int(line[0]), float(line[1]), float(line[2]))
                list_of_nodes.append(v)
                line_count += 1

            for l in f:
                line = l.strip().split()
                o_idx, e_idx = int(line[0]), int(line[1])
                origin = list_of_nodes[o_idx]
                end = list_of_nodes[e_idx]
                directed = line[2] == '1'
                origin.connect(end, directed, txt2int(line[3]), txt2int(line[4]), txt2int(line[5]))
                line_count += 1
        except:
            raise FileReadError(filename, line_count)
    return list_of_nodes

if __name__ == '__main__':
    L = [Node(i, i, 0) for i in range(4)]
    for i in range(4):
        L[i].connect(L[i-1], True, 5,cost = 3)
    L[1].connect(L[3], False, 10, cost = 2)
    L[1].connect(L[2], True, 7, cost = 5)
    graph_save(L, "test.txt")
    L2 = graph_read("test.txt")
    for v in L2:
        v.show()

