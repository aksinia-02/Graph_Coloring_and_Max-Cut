import argparse
import csv
import networkx as nx
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt
from tools import *

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

def max_difference_counter(counters):
    max_counter = max(counters)
    min_counter = min(counters)
    return max_counter - min_counter

def create_counter_for_colors(num_colors):
    return [0 for _ in range(num_colors)]

def is_safe(node, color, graph, coloring):
    for neighbor in graph.neighbors(node):
        if neighbor in coloring and coloring[neighbor] == color:
            return False
    return True


def backtrack_coloring(graph, node_index, max_colors, coloring):
    nodes = list(graph.nodes())

    if node_index == len(nodes):
        return True

    node = nodes[node_index]

    for color in range(1, max_colors + 1):
        if is_safe(node, color, graph, coloring):
            coloring[node] = color
            if backtrack_coloring(graph, node_index + 1, max_colors, coloring):
                return True
            coloring.pop(node)

    return False

def removeColorFromNeighbors(graph, node, color, colors_sets):
    neighbors = list(graph.neighbors(node))
    nodes = list(graph.nodes())
    for neighbor in neighbors:
        index = nodes.index(neighbor)
        if color in colors_sets[index]:
            colors_sets[index].remove(color)

def addColorFromNeighbors(graph, node, color, colors_sets):
    neighbors = list(graph.neighbors(node))
    nodes = list(graph.nodes())
    for neighbor in neighbors:
        index = nodes.index(neighbor)
        if color in colors_sets[index]:
            colors_sets[index].add(color)

def backtrack_coloring1(graph, node_index, max_colors, coloring, colors_sets, counters, n):
    nodes = list(graph.nodes())

    if node_index == len(nodes):
        return True

    node = nodes[node_index]

    colors = colors_sets[node_index].copy()

    for color in colors:
        flag = True
        if n > 0:
            counters[color - 1] = counters[color - 1] + 1
            if max_difference_counter(counters) > n:
                counters[color - 1] = counters[color - 1] - 1
                flag = False

        if flag:
            if color in colors_sets[node_index]:
                coloring[node] = color
                removeColorFromNeighbors(graph, node, color, colors_sets)
                if backtrack_coloring1(graph, node_index + 1, max_colors, coloring, colors_sets, counters, n):
                    return True
                if n > 0:
                    counters[color - 1] = counters[color - 1] - 1
                coloring.pop(node)
                addColorFromNeighbors(graph, node, color, colors_sets)
    return False


def exact_graph_coloring(graph, n):
    num_nodes = len(graph.nodes())
    low, high = 1, num_nodes
    result = num_nodes
    final_coloring = {}
    counters = {}

    while low <= high:
        mid = (low + high) // 2
        colors_sets = create_color_sets(num_nodes, mid)
        if n != 0:
            counters = create_counter_for_colors(mid)
        print(f"the number of colors are changed to {mid}")
        coloring = {}

        if backtrack_coloring1(graph, 0, mid, coloring, colors_sets, counters, n):
            result = mid
            final_coloring = coloring.copy()
            high = mid - 1
            print(f"the coloring is possible with {mid} colors, coloring {final_coloring}")
        else:
            low = mid + 1
            print(f"the coloring is NOT possible with {mid} colors")

    return result, final_coloring

def main():
    parser = argparse.ArgumentParser(description="Load a graph from a CSV file.")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to the CSV file.")
    parser.add_argument("-n", "--number", type=str, required=True, help="The number of difference for equitable coloring.")

    args = parser.parse_args()

    filename = args.file
    try:
        n = int(args.number)
    except ValueError:
        print(f"Error: '{args.number}' is not a valid number.")
        return

    G = read_from_csv_file(filename)
    print("Graph loaded:", G)

    chromatic_number, coloring = exact_graph_coloring(G, n)

    color_map = generate_color_map(chromatic_number)

    print(f"The final number of colors are {chromatic_number}")
    display_colored_graph(G, coloring, color_map)
    #visualize_colors(color_map)



if __name__ == "__main__":
    main()