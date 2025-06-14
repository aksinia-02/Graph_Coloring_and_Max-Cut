from graph_coloring.tools import display_colored_graph
import argparse
import csv
import networkx as nx
import matplotlib.cm as cm
import numpy as np

def read_from_csv_file(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        nodes = next(reader)
        adj_matrix = [list(map(int, row)) for row in reader]

    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    for i, row in enumerate(adj_matrix):
        for j, value in enumerate(row):
            if value:
                graph.add_edge(nodes[i], nodes[j])

    return graph

def generate_color_map(m):
    """Generate m distinct colors using a colormap."""
    colors = cm.rainbow(np.linspace(0, 1, m))  # Get m colors from the rainbow colormap
    color_map = {i + 1: "#{:02x}{:02x}{:02x}".format(
        int(colors[i][0] * 255),
        int(colors[i][1] * 255),
        int(colors[i][2] * 255)
    ) for i in range(m)}
    return color_map

def main():
    parser = argparse.ArgumentParser(description="Display graph.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file.")

    args = parser.parse_args()
    print(args)

    graph = read_from_csv_file(args.input)
    print("Graph loaded:", graph)

    color_map = generate_color_map(1)

    coloring = {}
    for node in graph.nodes():
        coloring[node] = 1

    display_colored_graph(graph, coloring, color_map)

if __name__ == "__main__":
    main()