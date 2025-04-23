from itertools import product
from collections import Counter
from max_cut.tools import calculate_cut_size


def invalid_partition_check_eq(partition, n):
    nodes_counts = Counter(partition.values())
    diff = max(nodes_counts.values()) - min(nodes_counts.values())
    return diff > n


def exact_max_cut(graph, n):
    nodes = list(graph.nodes())
    max_cut_size = 0
    best_partition = None

    len_first_part_partitions = (pow(2, len(nodes))) / 2
    print(len_first_part_partitions)

    for partition_bits in product([1, 2], repeat=len(nodes)):
        if len_first_part_partitions <= 0:
            break
        len_first_part_partitions -= 1
        partition = dict(zip(nodes, partition_bits))
        if n != -1:
            if invalid_partition_check_eq(partition, n):
                continue
        cut_size, cut = calculate_cut_size(graph, partition)

        if cut_size > max_cut_size:
            print(f"New MAX CUT: {cut_size}")
            max_cut_size = cut_size
            best_partition = partition

    return best_partition, max_cut_size
