import argparse
import csv
import networkx as nx
import matplotlib.cm as cm
import numpy as np
from max_cut.exact_max_cut import *
from max_cut.heuristic_max_cut import *
from collections import Counter
from max_cut.tools import display_colored_graph


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


def run_solving_max_cut(graph, n, opt):
    type_alg = "exact" if opt == 1 else "heuristic"
    print("------------------------------------")
    print(f"Start {type_alg} with diff {n}")
    print("------------------------------------")
    if opt == 1:
        max_cut_size, best_partition = exact_max_cut(graph, n)
    else:
        max_cut_size, best_partition = iterative_max_cut(graph, n)
    print(f"The final number of edges between sets is {max_cut_size}")
    return best_partition


def validate_number(value):
    int_value = int(value)
    if int_value < -1:
        raise argparse.ArgumentTypeError(f"Value must be greater than or equal to -1. You entered {int_value}.")
    return int_value


def main():
    parser = argparse.ArgumentParser(description="Load a graph from a CSV file.")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to the CSV file.")
    parser.add_argument("-n", "--number", type=validate_number, required=False, help="The number of difference for bisectional cut.")
    parser.add_argument("-o", "--optimal", type=int, choices=[0, 1], required=True, help="Set to 1 if an optimal solution is required, otherwise 0 for a heuristic solution.")

    args = parser.parse_args()
    print(args)

    filename = args.file

    graph = read_from_csv_file(filename)
    print("Graph loaded:", graph)

    n = args.number if args.number is not None else -1
    opt = args.optimal

    if opt == 1:
        best_partition, max_cut_size = exact_max_cut(graph, n)
    else:
        best_partition, max_cut_size = iterative_max_cut(graph, n)

    color_map = generate_color_map(2)

    print(f"The final number of edges between sets is {max_cut_size}")
    print(f"best_partition: {best_partition}")

    if best_partition is None:
        print(f"Partition with difference {n} is impossible")
    else:
        nodes_counts = Counter(best_partition.values())
        print(f"First set: {max(nodes_counts.values())}, second set: {min(nodes_counts.values())}")
        print(f"Difference is {max(nodes_counts.values()) - min(nodes_counts.values())}")

    #print_neighbors(graph)
        display_colored_graph(graph, best_partition, color_map)
    #visualize_colors(color_map)


if __name__ == "__main__":
    main()
