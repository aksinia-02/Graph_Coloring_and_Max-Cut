import networkx as nx
import matplotlib.pyplot as plt
import random
import csv
import string
import math
from tools import *

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

def generate_random_graph(nodes, p):
    G = nx.erdos_renyi_graph(nodes, p)

    if not nx.is_connected(G):
        G = connect_disconnected_components(G)

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = 2 * num_edges / num_nodes / (num_nodes - 1)

    if density >= 0.5:
        rem_edges = num_edges - math.ceil(num_nodes * (num_nodes - 1) / 4)
        print(f"num_nodes_pow: {num_nodes}, num_edges: {num_edges}, density: {density}, rem_edges: {rem_edges}")
        remove_random_edges(G, rem_edges)
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        density = 2 * num_edges / num_nodes / (num_nodes - 1)
        print(f"num_nodes_pow: {num_nodes}, num_edges: {num_edges}, density: {density}")
    return G

def save_into_csv_file(G, p):
    """Save the adjacency matrix of graph G into a CSV file."""
    n = len(G.nodes())
    m = len(G.edges())

    random_key = generate_random_key()
    dir_path = f"data/n_{n}_p_{int(p * 100)}"
    filename = f"{dir_path}/n_{n}_m_{m}_{random_key}.csv"

    adj_matrix = nx.adjacency_matrix(G).todense()

    adj_matrix_list = adj_matrix.tolist()

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(G.nodes())

        for row in adj_matrix_list:
            writer.writerow(row)

    print(f"New file {filename}")

def generate_and_save_25_graphs(n, p):
    for i in range(0, 24):
        sparse_graph = generate_random_graph(n, p)
        save_into_csv_file(sparse_graph, p)

#nodes = [25, 50, 100, 300]
# nodes = [200]
# prob = [0.1, 0.3, 0.5, 0.7]
#
# for n in nodes:
#     for p in prob:
#         generate_and_save_50_graphs(n, p)


# nodes = 7
# p = 1
#
# sparse_graph = generate_random_graph(nodes, p)
#
# display_graph(sparse_graph)
nodes = [60]
prob = [0.1]

for n in nodes:
    for p in prob:
        generate_and_save_25_graphs(n, p)
#
# plt.figure(figsize=(6, 6))
# nx.draw(sparse_graph, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500)
# plt.show()