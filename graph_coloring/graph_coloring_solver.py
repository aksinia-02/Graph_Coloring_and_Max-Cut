import argparse
from graph_coloring.exact_graph_coloring import *
from graph_coloring.heuristic_graph_coloring import *
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools
from tools import display_colored_graph
from tools import generate_color_map
from tools import read_from_csv_file

## python -m graph_coloring.graph_coloring_solver -f .\data_sparse\n_30_p_30\d_0.25_bIfpiUf1.csv -o 1 -n 1


def run_solving_graph_coloring(graph, n, opt, full_file_path, visualization=False, min_num_colors=7, max_num_colors=None):
    type_alg = "exact" if opt == 1 else "heuristic"
    print("------------------------------------")
    print(f"Start {type_alg} with diff {n}")
    print("------------------------------------")

    base_name = os.path.basename(full_file_path)
    json_name = base_name.replace(".csv", "")
    suffix = "_h" if opt == 0 else "_o"
    if n != -1:
        json_name = f"{json_name}{suffix}_n_{n}_coloring.json"
    else:
        json_name = f"{json_name}{suffix}_n_None_coloring.json"
    output_path = os.path.join(os.path.dirname(full_file_path), json_name)

    coloring = None
    chromatic_number = None

    if os.path.exists(output_path):
        print(f"Found existing coloring file: {output_path}. Loading coloring...")
        with open(output_path, "r") as f:
            coloring = json.load(f)

        chromatic_number = max(coloring.values()) if coloring else None

    else:
        if opt == 1:
            chromatic_number, coloring = exact_graph_coloring(graph, n, min_num_colors, max_num_colors)
        else:
            chromatic_number, coloring = heuristic_graph_coloring(graph, n)
        with open(output_path, "w") as f:
            json.dump(coloring, f, indent=4)
        print("------------------------------------")
        print(f"Coloring is saved to {output_path}")

    print("------------------------------------")
    print(f"The final number of colors is {chromatic_number}")
    color_counts = Counter(coloring.values())
    print(f"Max color class: {max(color_counts.values())}, Min color class: {min(color_counts.values())},"
          f" Color classes difference is {max(color_counts.values()) - min(color_counts.values())}")

    print("------------------------------------")
    if is_valid_coloring(graph, coloring):
        print("Coloring is VALID: No neighbors share the same color.")
    else:
        print("Coloring is INVALID: Some neighbors share the same color.")
    print("------------------------------------")

    if visualization:
        color_map = generate_color_map(chromatic_number)
        display_colored_graph(graph, coloring, color_map)

    return chromatic_number, coloring


def validate_number(value):
    int_value = int(value)
    if int_value < -1:
        raise argparse.ArgumentTypeError(f"Value must be greater than or equal to -1. You entered {int_value}.")
    return int_value


def is_valid_coloring(graph, coloring):
    for node in graph.nodes():
        for neighbor in graph.neighbors(node):
            if node in coloring and neighbor in coloring:
                if coloring[node] == coloring[neighbor]:
                    print(f"Invalid coloring: Node {node} and Node {neighbor} have the same color {coloring[node]}")
                    return False
    return True


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

    run_solving_graph_coloring(graph, n, opt, filename, visualization=True)


if __name__ == "__main__":
    main()
