import random
import csv
import string
import math
from graph_coloring.tools import *
import argparse
import os

def generate_random_key(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def connect_disconnected_components(G):
    components = list(nx.connected_components(G))
    while len(components) > 1:
        comp1 = random.choice(components)
        comp2 = random.choice([c for c in components if c != comp1])

        node1 = random.choice(list(comp1))
        node2 = random.choice(list(comp2))

        G.add_edge(node1, node2)

        components = list(nx.connected_components(G))
    return G

def remove_random_edges(G, num_edges_to_remove):
    edges = list(G.edges)
    removed_edges = 0

    while removed_edges < num_edges_to_remove and len(edges) > 0:
        edge = random.choice(edges)
        G.remove_edge(*edge)

        if nx.is_connected(G):
            removed_edges += 1
            edges.remove(edge)
        else:
            G.add_edge(*edge)
    print(f"Removed {num_edges_to_remove} edges to maintain sparsity.")

def cal_density_and_rem_adges(G):
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = 2 * num_edges / num_nodes / (num_nodes - 1)

    rem_edges = None

    if density >= 0.5:
        rem_edges = num_edges - math.ceil(num_nodes * (num_nodes - 1) / 4)

    return density, rem_edges

def generate_random_graph(nodes, p):
    G = nx.erdos_renyi_graph(nodes, p)

    if not nx.is_connected(G):
        G = connect_disconnected_components(G)

    density, rem_edges = cal_density_and_rem_adges(G)

    if rem_edges is not None:
        remove_random_edges(G, rem_edges)

    return G

def save_into_csv_file(G, p):
    """Save the adjacency matrix of graph G into a CSV file."""
    n = G.number_of_nodes()
    density, _ = cal_density_and_rem_adges(G)
    density = round(density, 2)

    random_key = generate_random_key()
    dir_path = f"data/n_{n}_p_{int(p * 100)}"
    os.makedirs(dir_path, exist_ok=True)
    filename = f"{dir_path}/d_{density}_{random_key}.csv"

    adj_matrix = nx.adjacency_matrix(G).todense()

    adj_matrix_list = adj_matrix.tolist()

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(G.nodes())

        for row in adj_matrix_list:
            writer.writerow(row)

    print(f"New file {filename}")

def generate_and_save_n_graphs(n, num_nodes, p):
    for _ in range(0, n):
        sparse_graph = generate_random_graph(num_nodes, p)
        save_into_csv_file(sparse_graph, p)

def main():
    parser = argparse.ArgumentParser(description="Generate the sparse random graphs.")
    parser.add_argument("-n", "--graphs", type=int, required=True, help="The number of graphs.")
    parser.add_argument("-nd", "--nodes", type=int, required=True, nargs="+",
                        help="The number of nodes. You can use array or single value.")
    parser.add_argument("-p", "--probabilities", type=float, required=True, nargs="+",
                        help="The probability that edge between between nodes exists. You can use array or single value between 0 and 1.")

    args = parser.parse_args()
    print(args)

    for p in args.probabilities:
        if (p < 0) or (p > 1):
            print(f"Probability must be the value between 0 and 1. Your value is {p}")
            return

    for nd in args.nodes:
        for p in args.probabilities:
            generate_and_save_n_graphs(args.graphs, nd, p)

if __name__ == "__main__":
    main()