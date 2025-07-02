from itertools import product
from collections import Counter
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools
from tools import calculate_cut_size

def bit_positions_set(x):
    """Yield all bit positions (0-based) that are set in integer x."""
    pos = 0
    while x > 0:
        if x & 1:
            yield pos
        x >>= 1
        pos += 1


def exact_max_cut(graph, n):
    nodes = list(graph.nodes())
    num_nodes = len(nodes)

    if n == 0 and (num_nodes % 2 != 0):
        return None, 0
    node_indices = {i: nodes[i] for i in range(num_nodes)}

    # Initialize with all zeros (partition to group 1)
    curr_state = 0
    partition = {node_indices[i]: 1 for i in range(num_nodes)}
    partition_sizes = {1: num_nodes, 2: 0}

    # Initial cut size
    cut_size, cut = calculate_cut_size(graph, partition)
    max_cut_size = cut_size
    best_partition = partition.copy()

    total_states = 1 << (num_nodes - 1)
    progress_interval = total_states // 10
    for next_state in range(1, total_states):
        if next_state % progress_interval == 0:
            percent = (next_state * 100) // total_states
            print(f"Progress: {percent}%")
        changed = curr_state ^ next_state
        flipped_bits = list(bit_positions_set(changed))

        for flip_index in flipped_bits:
            flipped_node = node_indices[flip_index]
            old_group = partition[flipped_node]
            new_group = 2 if old_group == 1 else 1

            # Update partition sizes and partition
            partition_sizes[old_group] -= 1
            partition_sizes[new_group] += 1
            partition[flipped_node] = new_group

            # Incrementally update cut size
            for neighbor in graph.neighbors(flipped_node):
                if partition[neighbor] == new_group:
                    cut_size -= 1
                else:
                    cut_size += 1
        # Balance check
        if n != -1:
            diff = abs(partition_sizes[1] - partition_sizes[2])
            if diff > n:
                curr_state = next_state
                continue

        if cut_size > max_cut_size:
            print(f"New MAX CUT: {cut_size}")
            max_cut_size = cut_size
            best_partition = partition.copy()

        curr_state = next_state

    return best_partition, max_cut_size

def exact_max_cut_multi_n(graph, max_diff=5):
    nodes = list(graph.nodes())
    num_nodes = len(nodes)

    node_indices = {i: nodes[i] for i in range(num_nodes)}

    curr_state = 0
    partition = {node_indices[i]: 1 for i in range(num_nodes)}
    partition_sizes = {1: num_nodes, 2: 0}

    cut_size, _ = calculate_cut_size(graph, partition)

    # Track max cut and partition for each n (0 to max_diff) and -1 (unbounded)
    tracked_ns = list(range(max_diff + 1)) + [-1]
    results = {
        n: {"cut_size": cut_size, "partition": partition.copy()}
        for n in tracked_ns
    }

    if (num_nodes % 2 != 0):
        results[0]["cut_size"] = 0
        results[0]["partition"] = None

    total_states = 1 << (num_nodes - 1)
    progress_interval = max(1, total_states // 10)
    print(f"Progress: {0}%")

    for next_state in range(1, total_states):
        if next_state % progress_interval == 0:
            percent = (next_state * 100) // total_states
            print(f"Progress: {percent}%")

        changed = curr_state ^ next_state
        flipped_bits = list(bit_positions_set(changed))

        for flip_index in flipped_bits:
            flipped_node = node_indices[flip_index]
            old_group = partition[flipped_node]
            new_group = 2 if old_group == 1 else 1

            # Update partition
            partition_sizes[old_group] -= 1
            partition_sizes[new_group] += 1
            partition[flipped_node] = new_group

            for neighbor in graph.neighbors(flipped_node):
                if partition[neighbor] == new_group:
                    cut_size -= 1
                else:
                    cut_size += 1

        # Check current balance
        imbalance = abs(partition_sizes[1] - partition_sizes[2])

        for n in tracked_ns:
            if n == -1 or imbalance <= n:
                if cut_size > results[n]["cut_size"]:
                    results[n]["cut_size"] = cut_size
                    results[n]["partition"] = partition.copy()

        curr_state = next_state

    return results