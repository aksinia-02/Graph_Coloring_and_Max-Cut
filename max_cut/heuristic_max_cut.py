import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools
from tools import calculate_cut_size


def iterative_max_cut(graph, max_iterations=1000):
    nodes = list(graph.nodes())
    partition = {node: random.choice([0, 1]) for node in nodes}
    current_cut_size, _ = calculate_cut_size(graph, partition)

    for _ in range(max_iterations):
        improved = False

        for node in nodes:
            partition[node] = 1 - partition[node]
            new_cut_size, _ = calculate_cut_size(graph, partition)

            if new_cut_size > current_cut_size:
                current_cut_size = new_cut_size
                improved = True
            else:
                partition[node] = 1 - partition[node]

        if not improved:
            break

    partition = {node: value + 1 for node, value in partition.items()}

    return partition, current_cut_size
