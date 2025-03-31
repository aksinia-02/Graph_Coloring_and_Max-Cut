import argparse
import csv
import networkx as nx
import matplotlib.cm as cm
import numpy as np
import time
from exact_graph_coloring import *
from DSATUR_graph_coloring import *


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


def run_solving(graph, n, opt):
    type_alg = "exact" if opt == 1 else "DSATUR"
    print("------------------------------------")
    print(f"Start {type_alg} with diff {n}")
    print("------------------------------------")

    if opt == 1:
        chromatic_number, coloring = exact_graph_coloring(graph, n)
    else:
        chromatic_number, coloring = dsatur_graph_coloring(graph, n)
    print(f"The final number of colors is {chromatic_number}")
    return chromatic_number


def validate_number(value):
    int_value = int(value)
    if int_value < -1:
        raise argparse.ArgumentTypeError(f"Value must be greater than or equal to -1. You entered {int_value}.")
    return int_value


def main():
    parser = argparse.ArgumentParser(description="Load a graph from a CSV file.")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to the CSV file.")
    parser.add_argument("-n", "--number", type=validate_number, required=False, help="The number of difference for equitable coloring.")
    parser.add_argument("-o", "--optimal", type=int, choices=[0, 1], required=True, help="Set to 1 if an optimal solution is required, otherwise 0 for a heuristic solution.")

    args = parser.parse_args()
    print(args)

    filename = args.file

    graph = read_from_csv_file(filename)
    print("Graph loaded:", graph)

    n = args.number if args.number is not None else -1
    opt = args.optimal

    if opt == 1:
        chromatic_number, coloring = exact_graph_coloring(graph, n)
    else:
        chromatic_number, coloring = dsatur_graph_coloring(graph, n)
        # coloring = nx.coloring.greedy_color(graph, strategy="DSATUR")
        # coloring = {node: color + 1 for node, color in coloring.items()}
        # chromatic_number = max(coloring.values())

    color_map = generate_color_map(chromatic_number)

    print(f"The final number of colors is {chromatic_number}")
    print(f"coloring: {coloring}")

    print_neighbors(graph)
    display_colored_graph(graph, coloring, color_map)
    #visualize_colors(color_map)


if __name__ == "__main__":
    main()
