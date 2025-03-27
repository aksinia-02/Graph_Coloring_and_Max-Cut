import argparse
import csv
import networkx as nx
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt
from tools import *
import time

def read_from_csv_file(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        nodes = next(reader)
        adj_matrix = [list(map(int, row)) for row in reader]

    G = nx.Graph()
    G.add_nodes_from(nodes)

    for i, row in enumerate(adj_matrix):
        for j, value in enumerate(row):
            if value:
                G.add_edge(nodes[i], nodes[j])

    return G

def generate_color_map(m):
    """Generate m distinct colors using a colormap."""
    colors = cm.rainbow(np.linspace(0, 1, m))  # Get m colors from the rainbow colormap
    color_map = {i + 1: "#{:02x}{:02x}{:02x}".format(
        int(colors[i][0] * 255),
        int(colors[i][1] * 255),
        int(colors[i][2] * 255)
    ) for i in range(m)}
    return color_map


def create_color_sets(num_nodes, num_colors):
    return [set(range(1, num_colors + 1)) for _ in range(num_nodes)]

def balance_colors(counters, n_nodes, n):
    # optimisation by available colors
    colored_nodes = sum(counters)
    uncolored_nodes = n_nodes - colored_nodes

    num_colors = len(counters)

    max_counter = max(counters)

    added = 0
    for i in range(num_colors):
        diff = max_counter - counters[i]
        diff_n = diff - n
        if diff_n > 0:
            added += diff_n
        if added > uncolored_nodes:
            #print(f"uncolored_nodes: {uncolored_nodes}, added: {added}")
            return False

    return True

def create_counter_for_colors(num_colors):
    return [0 for _ in range(num_colors)]

def removeColorFromNeighbors(graph, node, color, colors_sets):
    neighbors = list(graph.neighbors(node))
    nodes = list(graph.nodes())
    for neighbor in neighbors:
        index = nodes.index(neighbor)
        if color in colors_sets[index]:
            colors_sets[index].remove(color)
    # index_node = nodes.index(node)
    # if color in colors_sets[index_node]:
    #     colors_sets[index_node].remove(color)

def addColorFromNeighbors(graph, node, color, colors_sets, coloring):
    neighbors = list(graph.neighbors(node))
    nodes = list(graph.nodes())
    flag = True
    for neighbor in neighbors:
        neighbors_for_neighbor = list(graph.neighbors(neighbor))
        for n_f_n in neighbors_for_neighbor:
            index_n_f_n = nodes.index(n_f_n)
            #print(f"index: {index_n_f_n}, coloring: {coloring}")
            #print(f"neighbor color: {coloring.get(str(index_n_f_n))}, color to remove: {color}")
            if coloring.get(str(index_n_f_n)) == color:
                flag = False
        if flag:
            index = nodes.index(neighbor)
            if color not in colors_sets[index]:
                colors_sets[index].add(color)
    # index_node = nodes.index(node)
    # if color not in colors_sets[index_node]:
    #     colors_sets[index_node].add(color)


def backtrack_coloring(graph, node_index, max_colors, coloring, colors_sets, counters, n, sorted_node_indices):
    nodes = list(graph.nodes())

    if node_index == len(nodes):
        return True

    node_index_sorted = int(sorted_node_indices[node_index])

    node = nodes[node_index_sorted]

    colors = colors_sets[node_index_sorted].copy()

    for color in colors:
        #print(f"node: {node}, color: {color}")
        # if node_index == 0:
        #     #print(color)
        #     print(f"index: {node_index}")
        #     print(f"coloring: {coloring}")
        #     print(f"counters: {counters}")
        flag = True
        if n != -1:
            counters[color - 1] = counters[color - 1] + 1
            #print(f"{color - 1} {counters}")
            if not balance_colors(counters, graph.number_of_nodes(), n):
                counters[color - 1] = counters[color - 1] - 1
                # print(f"-{color - 1}          not balanced")
                # print(counters)
                flag = False

        if flag:
            if color in colors_sets[node_index_sorted]:
                coloring[node] = color
                # print(f"add into coloring: {coloring}")
                removeColorFromNeighbors(graph, node, color, colors_sets)
                # print(colors_sets)
                # print(f"remove color {color} from neighbors")
                if backtrack_coloring(graph, node_index + 1, max_colors, coloring, colors_sets, counters, n, sorted_node_indices):
                    return True
                if n != -1:
                    counters[color - 1] = counters[color - 1] - 1
                    # print(f"-{color - 1} node: {node}          backtrack_coloring")
                    # print(counters)
                coloring.pop(node)
                #print(f"pop from coloring: {coloring}")
                addColorFromNeighbors(graph, node, color, colors_sets, coloring)
                # print(colors_sets)
                # print(f"add color {color} to neighbors")
            else:
                if n != -1:
                    counters[color - 1] = counters[color - 1] - 1
                    # print(f"-{color - 1}          color is not available")
                    # print(counters)
    return False


def sorted_nodes_by_degree(graph):
    node_degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes()]
    sorted_nodes = sorted(node_degree, key=lambda x: x[1], reverse=True)
    sorted_node_indices = [node for node, _ in sorted_nodes]

    return sorted_node_indices


def exact_graph_coloring(graph, n):
    num_nodes = len(graph.nodes())
    low, high = 1, num_nodes
    result = num_nodes
    final_coloring = {}
    counters = {}

    sorted_node_indices = sorted_nodes_by_degree(graph)

    while low <= high:
        mid = (low + high) // 2
        colors_sets = create_color_sets(num_nodes, mid)
        if n != -1:
            counters = create_counter_for_colors(mid)
        print(f"the number of colors are changed to {mid}")
        coloring = {}

        if backtrack_coloring(graph, 0, mid, coloring, colors_sets, counters, n, sorted_node_indices):
            result = mid
            final_coloring = coloring.copy()
            high = mid - 1
            print(f"the coloring is possible with {mid} colors, coloring {final_coloring}")
        else:
            low = mid + 1
            print(f"the coloring is NOT possible with {mid} colors")

    return result, final_coloring

def print_neighbors(G):
    for node in G.nodes:
        neighbors = G.neighbors(node)
        result =""
        for neighbor in neighbors:
            result += neighbor
            result += ","
        print(f"node: {node}, neighbors: {result}")
        print("")

def main():
    parser = argparse.ArgumentParser(description="Load a graph from a CSV file.")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to the CSV file.")
    parser.add_argument("-n", "--number", type=int, required=False, help="The number of difference for equitable coloring.")

    args = parser.parse_args()
    print(args)

    filename = args.file

    G = read_from_csv_file(filename)
    print("Graph loaded:", G)

    n = args.number if args.number is not None else -1
    if n < -1:
        print(f"The number of difference for equitable coloring must be >= 0. Your value is {n}")

    chromatic_number, coloring = exact_graph_coloring(G, n)

    color_map = generate_color_map(chromatic_number)

    print(f"The final number of colors are {chromatic_number}")
    print(f"coloring: {coloring}")

    display_colored_graph(G, coloring, color_map)
    #visualize_colors(color_map)



if __name__ == "__main__":
    main()