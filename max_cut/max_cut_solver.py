import argparse
from max_cut.exact_max_cut import *
from max_cut.heuristic_max_cut import *
from collections import Counter
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools
from tools import display_colored_graph
from tools import generate_color_map
from tools import read_from_csv_file

def run_solving_max_cut(graph, n, opt, full_file_path, visualization=False):
    type_alg = "exact" if opt == 1 else "heuristic"
    print("------------------------------------")
    print(f"Start {type_alg} with diff {n}")
    print("------------------------------------")

    base_name = os.path.basename(full_file_path)
    json_name = base_name.replace(".csv", "")
    suffix = "_h" if opt == 0 else "_o"
    if n == -1:
        json_name = f"{json_name}{suffix}_n_None_max_cut.json"
    else:
        json_name = f"{json_name}{suffix}_n_{n}_max_cut.json"
    output_path = os.path.join(os.path.dirname(full_file_path), json_name)

    best_partition = None
    max_cut_size = None

    if os.path.exists(output_path):
        print(f"Found existing partition file: {output_path}. Loading...")
        with open(output_path, "r") as f:
            data = json.load(f)
            best_partition = data.get("partition")
            max_cut_size = data.get("max_cut_size")

    else:
        if opt == 1:
            best_partition, max_cut_size = exact_max_cut(graph, n)
        else:
            best_partition, max_cut_size = iterative_max_cut(graph, n)
            print(f"Partition: {best_partition}")

        with open(output_path, "w") as f:
            json.dump({
                "partition": best_partition,
                "max_cut_size": max_cut_size
            }, f, indent=4)
        print("------------------------------------")
        print(f"Partition is saved to {output_path}")

    if best_partition is None:
        print("------------------------------------")
        print(f"Partition with difference {n} is impossible")

    print("------------------------------------")
    print(f"MAX CUT is {max_cut_size}")

    if best_partition is not None:
        nodes_counts = Counter(best_partition.values())
        print("------------------------------------")
        print(f"First set: {max(nodes_counts.values())}, second set: {min(nodes_counts.values())}")
        print(f"Difference is {max(nodes_counts.values()) - min(nodes_counts.values())}")

    if visualization:
        color_map = generate_color_map(2)
        display_colored_graph(graph, best_partition, color_map)

    return max_cut_size, best_partition

def validate_number(value):
    int_value = int(value)
    if int_value < -1:
        raise argparse.ArgumentTypeError(f"Value must be greater than or equal to -1. You entered {int_value}.")
    return int_value


def main():
    parser = argparse.ArgumentParser(description="Load a graph from a CSV file.")
    parser.add_argument("-f", "--file", type=str, required=True, help="Path to the CSV file.")
    parser.add_argument("-n", "--number", type=validate_number, required=False, help="The difference between partitions.")
    parser.add_argument("-o", "--optimal", type=int, choices=[0, 1], required=True, help="Set to 1 if an optimal solution is required, otherwise 0 for a heuristic solution.")
    args = parser.parse_args()
    print(args)

    filename = args.file

    graph = read_from_csv_file(filename)
    print("Graph loaded:", graph)

    n = args.number if args.number is not None else -1
    opt = args.optimal

    run_solving_max_cut(graph, n, opt, filename, visualization=True)


if __name__ == "__main__":
    main()
