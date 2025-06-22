import random
import sys
import os
from collections import Counter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools
from tools import calculate_cut_size

def invalid_partition_check_eq(partition, n):
    nodes_counts = Counter(partition.values())
    diff = max(nodes_counts.values()) - min(nodes_counts.values())
    return diff > n


def iterative_max_cut(graph, n, max_iterations=1000):
    nodes = list(graph.nodes())
    partition = {node: random.choice([0, 1]) for node in nodes}
    current_cut_size, _ = calculate_cut_size(graph, partition)

    for _ in range(max_iterations):
        improved = False

        for node in nodes:
            partition[node] = 1 - partition[node]

            if n != -1 and invalid_partition_check_eq(partition, n):
                partition[node] = 1 - partition[node]  # Revert due to imbalance
                continue
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
