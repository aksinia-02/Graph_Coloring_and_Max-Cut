from itertools import product
from collections import Counter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools
from tools import calculate_cut_size


def invalid_partition_check_eq(partition, n):
    nodes_counts = Counter(partition.values())
    diff = max(nodes_counts.values()) - min(nodes_counts.values())
    return diff > n

def gray_code(n):
    """Generates Gray code sequence of n bits."""
    for i in range(1 << n):
        yield i ^ (i >> 1)


def bit_position_change(prev, curr):
    """Returns the index of the bit that changed between two Gray codes."""
    return (prev ^ curr).bit_length() - 1


def exact_max_cut(graph, n):
    nodes = list(graph.nodes())
    num_nodes = len(nodes)

    if n == 0 and (num_nodes % 2 != 0):
        return None, 0
    node_indices = {i: nodes[i] for i in range(num_nodes)}

    # Initialize with all zeros (partition to group 1)
    curr_code = 0
    partition = {node_indices[i]: 1 for i in range(num_nodes)}

    # Initial cut size
    cut_size, cut = calculate_cut_size(graph, partition)
    max_cut_size = cut_size
    best_partition = partition.copy()

    for next_code in gray_code(num_nodes):
        if (next_code & 1) == 1:
            curr_code = next_code
            continue

        flip_index = bit_position_change(curr_code, next_code)
        if flip_index == -1:
            curr_code = next_code
            continue
        flipped_node = node_indices[flip_index]

        # Flip the node's partition
        partition[flipped_node] = 2 if partition[flipped_node] == 1 else 1

        # Incrementally update cut size
        for neighbor in graph.neighbors(flipped_node):
            if partition[neighbor] == partition[flipped_node]:
                cut_size -= 1
            else:
                cut_size += 1

        # Balance check
        if n != -1 and invalid_partition_check_eq(partition, n):
            curr_code = next_code
            continue

        if cut_size > max_cut_size:
            print(f"New MAX CUT: {cut_size}")
            max_cut_size = cut_size
            best_partition = partition.copy()

        curr_code = next_code

    return best_partition, max_cut_size
