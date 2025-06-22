import random
import csv
import string
import math
from tools import *
import argparse
import os


def generate_random_key(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_seed():
    seed = random.randint(0, 2 ** 32 - 1)
    return seed


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


def cal_density(G):
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = 2 * num_edges / num_nodes / (num_nodes - 1)

    return density


def generate_random_graph(nodes, p=None, val_2=None):
    if p is None:
        p = float(input("Enter a probability between 0 and 1: "))
    while not isinstance(p, (int, float)) or p < 0 or p > 1:
        try:
            p = float(input("Invalid probability! Enter a value between 0 and 1: "))
        except ValueError:
            continue

    G = nx.erdos_renyi_graph(nodes, p, seed=generate_random_seed())

    if not nx.is_connected(G):
        G = connect_disconnected_components(G)

    return p, None, G


## scale free network has a degree distribution which follows a power low
def generate_scale_free_graph(n, m=None, val_2=None):
    if m is None:
        m = int(input(f"Enter the number of nodes for small connected seed graph > 0 and > {n - 1}: "))
    while not isinstance(m, int) or (n < m + 1) < 0 or m == 0:
        try:
            m = int(input(f"Invalid number of nodes! Enter a value > 0 and > {n - 1}: "))
        except ValueError:
            continue
    return m, None, nx.barabasi_albert_graph(n, m, seed=generate_random_seed())


# Create graphs with high clustering and short path lengths
def generate_small_world_graph(n, k=None, p=None):
    if k is None:
        k = int(input(f"Enter k (even integer < {n}): "))
    while not isinstance(k, int) or k <= 0 or k >= n or k % 2 != 0:
        try:
            k = int(input(f"Invalid input! Enter k (even integer < {n}): "))
        except ValueError:
            continue
    if p is None:
        p = float(input("Enter rewiring probability between 0 and 1: "))
    while not isinstance(p, (int, float)) or p < 0 or p > 1:
        try:
            p = float(input("Invalid probability! Enter a value between 0 and 1: "))
        except ValueError:
            continue
    return k, p, nx.watts_strogatz_graph(n, k, p, seed=generate_random_seed())


# 2D grid graphs, which are planar and useful for certain coloring problems
# creates a graph where nodes are placed in an m × n grid.
# Each node is a coordinate tuple: (i, j) where 0 ≤ i < m and 0 ≤ j < n
def generate_planar_graph(nodes, m=None, n=None):
    if n is None:
        n = int(input("Enter number of rows (n > 0): "))
    while not isinstance(n, int) or n <= 0:
        try:
            n = int(input(f"Invalid input! Enter number of rows (n > 0): "))
        except ValueError:
            continue
    if m is None:
        m = int(input("Enter number of columns (m > 0): "))
    while not isinstance(n, int) or n <= 0:
        try:
            m = int(input(f"Invalid input! Enter number of columns (m > 0): "))
        except ValueError:
            continue
    return m, n, nx.grid_2d_graph(n, m)

def generate_complete_bipartite_graph(nodes, n1=None, n2=None):
    if n1 is None:
        n1 = int(input("Enter number of nodes in first partition range(n1), n1 > 0: "))
    while not isinstance(n1, int) or n1 <= 0:
        try:
            n1 = int(input(f"Invalid input! Enter number of nodes in first partition range(n1), n1 > 0: "))
        except ValueError:
            continue
    if n2 is None:
        n2 = int(input("Enter number of nodes in second partition range(n1, n1 + n2), n2 > 0: "))
    while not isinstance(n2, int) or n2 <= 0:
        try:
            n2 = int(input(f"Invalid input! Enter number of nodes in second partition range(n1, n1 + n2), n2 > 0: "))
        except ValueError:
            continue

    return n1, n2, nx.complete_bipartite_graph(n1, n2)

def get_partition_sizes_from_user():
    partition_sizes = []
    print("Enter partition sizes one by one. Press Enter (empty input) to finish.")
    while True:
        inp = input(f"Partition size #{len(partition_sizes)+1}: ")
        if inp == "":
            break
        try:
            size = int(inp)
            if size <= 0:
                print("Partition size must be a positive integer.")
                continue
            partition_sizes.append(size)
        except ValueError:
            print("Please enter a valid integer.")
    return partition_sizes

def generate_complete_k_partite_graph(nodes):
    partition_sizes = get_partition_sizes_from_user()
    total_nodes = sum(partition_sizes)
    print(f"Total nodes in the graph: {total_nodes}")
    G = nx.Graph()
    partitions = []
    start = 0

    result = ""
    for size in partition_sizes:
        result += f"{size}_"
    result = result.rstrip("-")
    for size in partition_sizes:
        group = range(start, start + size)
        partitions.append(group)
        start += size
        G.add_nodes_from(group)

    for i, p1 in enumerate(partitions):
        for p2 in partitions[i + 1:]:
            G.add_edges_from((u, v) for u in p1 for v in p2)
    return result, None, G


def get_community_structure_from_user():
    print("Enter community sizes one by one. Press Enter with no input to finish.")
    sizes = []

    while True:
        inp = input(f"Size of community #{len(sizes) + 1}: ")
        if inp == "":
            break
        try:
            size = int(inp)
            if size <= 0:
                print("Community size must be a positive integer.")
                continue
            sizes.append(size)
        except ValueError:
            print("Invalid input! Please enter a valid integer.")

    if len(sizes) < 2:
        print("At least two communities are required.")
        return get_community_structure_from_user()

    print("Intra- the probability that two nodes from the same community are connected")

    while True:
        try:
            intra = float(input("Enter intra-community edge probability (0 < p ≤ 1): "))
            if 0 < intra <= 1:
                break
            else:
                print("Value must be > 0 and ≤ 1.")
        except ValueError:
            print("Invalid input! Please enter a float value.")

    print("Inter- the probability that two nodes from different communities are connected")

    while True:
        try:
            inter = float(input("Enter inter-community edge probability (0 ≤ p < intra): "))
            if 0 <= inter < intra:
                break
            else:
                print(f"Value must be ≥ 0 and < intra-community probability ({intra}).")
        except ValueError:
            print("Invalid input! Please enter a float value.")

    # Build probability matrix
    n = len(sizes)
    p_matrix = [[intra if i == j else inter for j in range(n)] for i in range(n)]

    return sizes, p_matrix, intra, inter

def generate_clustered_graph(nodes):

    sizes, p_matrix, intra, inter = get_community_structure_from_user()

    print(p_matrix)

    sizes_string = "_".join(str(size) for size in sizes)
    sizes_string = "com_sizes_" + sizes_string
    intra_inter = f"intra_{intra}_inter_{inter}"

    return sizes_string, intra_inter, nx.stochastic_block_model(sizes, p_matrix, seed=generate_random_seed())


def generate_random_regular_graph(nodes, d=None, val_2=None):
    if not d:
        d = int(input(f"Enter the degree of each node, d > 0. {nodes} * d must be even: "))
        while not isinstance(d, int) or d <= 0 or (nodes * d) % 2 == 1:
            try:
                d = int(input(f"Invalid input! Enter the degree of each node, d > 0: "))
            except ValueError:
                continue

    return d, None, nx.random_regular_graph(d, nodes, seed=generate_random_seed())

def save_into_csv_file(G, f, val_1, val_2, graph_type):
    """Save the adjacency matrix of graph G into a CSV file."""
    n = G.number_of_nodes()
    density = cal_density(G)
    density = round(density, 2)

    graph_values = {
        'r': ['p'],
        'w': ['k', 'p'],
        'f': ['m'],
        'p': ['m'],
        'b': None,
        'k': None,
        'rr': None,
        'c': None,
    }

    random_key = generate_random_key()

    keys = graph_values.get(graph_type, [])
    dir_path = f"input/{f}/n_{n}"
    if graph_type == "p":
        dir_path = f"input/{f}/n_{val_2}"
    if keys:
        dir_path += f"_{keys[0]}_{val_1}"
        if graph_type != "p" and val_2 is not None and len(keys) > 1:
            dir_path += f"_{keys[1]}_{val_2}"
    filename = f"{dir_path}/d_{density}_{random_key}.csv"
    if graph_type == "p":
        dir_path = f"input/{f}/planar_graphs"
        filename = f"{dir_path}/n_{val_1}_m_{val_2}_d_{density}_{random_key}.csv"
    if graph_type == "b":
        dir_path = f"input/{f}/bipartite_graph"
        filename = f"{dir_path}/n1_{val_1}_n2_{val_2}_d_{density}_{random_key}.csv"
    if graph_type == "k":
        dir_path = f"input/{f}/k_partite_graph"
        filename = f"{dir_path}/per_{val_1}_d_{density}_{random_key}.csv"
    if graph_type == "rr":
        dir_path = f"input/{f}/regular_graph"
        filename = f"{dir_path}/n_{n}_deg_{val_1}_d_{density}_{random_key}.csv"
    if graph_type == "c":
        dir_path = f"input/{f}/clustered_graph"
        filename = f"{dir_path}/{val_1}_{val_2}_{random_key}.csv"

    os.makedirs(dir_path, exist_ok=True)

    adj_matrix = nx.adjacency_matrix(G).todense()

    adj_matrix_list = adj_matrix.tolist()

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(G.nodes())

        for row in adj_matrix_list:
            writer.writerow(row)

    print(f"New file {filename}")


def generate_and_save_n_graphs(graph_type, k, n, f, val_1, val_2):
    graph_generators = {
        'r': generate_random_graph,
        'w': generate_small_world_graph,
        'f': generate_scale_free_graph,
        'p': generate_planar_graph,
        'b': generate_complete_bipartite_graph,
        'k': generate_complete_k_partite_graph,
        'rr': generate_random_regular_graph,
        'c': generate_clustered_graph
    }

    graph_func = graph_generators.get(graph_type, lambda: print("Unknown graph type."))

    for _ in range(0, k):
        if graph_type not in ["b", "k", "c", "p"]:
            val_1, val_2, graph = graph_func(n, val_1, val_2)
        else:
            val_1, val_2, graph = graph_func(n)
        save_into_csv_file(graph, f, val_1, val_2, graph_type)

    return val_1, val_2


# python .\random_graph_generator.py -n 10 -nd 10 20 30 40 50 60 70 80 100 -p 0.6 0.8 1 -s 0 -f data_dense

#  python .\random_graph_generator.py -k 10 -n 10 30 50 70 90 -f random_graph

def main():
    parser = argparse.ArgumentParser(description="Generate some random graphs.")
    parser.add_argument("-k", "--graphs", type=int, required=True, help="The number of graphs.")
    parser.add_argument("-f", "--folder_name", type=str, required=True,
                        help="Folder name for output.")

    args = parser.parse_args()
    print(args)

    print("Select graph type to generate:")
    print("r: random graph (Erdős-Rényi)")
    print("w: small-world network (Watts-Strogatz)")
    print("f: scale-free network (Barabási-Albert)")
    print("p: planar grid graph")
    print("b: complete bipartite graph")
    print("k: complete k partite graph")
    print("rr: random regular graph")
    print("c: community / clustered graph")

    flag = True
    graph_type = None
    nodes = None
    while flag:
        graph_type = input("Enter your choice (r/w/f/p/b/k/rr/c): ").strip().lower()
        if graph_type not in {'r', 'w', 'f', 'p', 'b', 'k', 'rr', 'c'}:
            print("Invalid graph type selected. Please enter one of: r, w, f, p, b, k, rr, c")
        else:
            flag = False
    if graph_type in {"r", "w", "f", "rr"}:
        print("Enter the number of nodes one by one. Graphs will be created in loop. "
              "Press Enter with no input to finish.")
        nodes = []

        while True:
            inp = input(f"Enter the number of nodes: ")
            if inp == "":
                break
            try:
                node = int(inp)
                if node <= 0:
                    print("The number of nodes must be a positive integer.")
                    continue
                nodes.append(node)
            except ValueError:
                print("Invalid input! Please enter a valid integer.")

    val_1 = None
    val_2 = None

    if nodes is not None:
        for n in nodes:
            val_1, val_2 = generate_and_save_n_graphs(graph_type, args.graphs, n, args.folder_name, val_1, val_2)
    else:
        generate_and_save_n_graphs(graph_type, args.graphs, nodes, args.folder_name, val_1, val_2)


if __name__ == "__main__":
    main()
