import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools
from tools import display_colored_graph
from tools import generate_color_map
from tools import read_from_csv_file

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