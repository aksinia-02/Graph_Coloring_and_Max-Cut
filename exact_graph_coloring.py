from tools import *
import copy


def balance_colors(counters, n_nodes, n):
    # optimisation by available colors
    colored_nodes = sum(counters)
    uncolored_nodes = n_nodes - colored_nodes

    num_colors = len(counters)

    max_counter = max(counters)

    added = 0
    for i in range(num_colors):
        diff = max_counter - counters[i]
        diff_n = diff - n
        if diff_n > 0:
            added += diff_n
        if added > uncolored_nodes:
            return False

    return True


def create_counter_for_colors(num_colors):
    return [0 for _ in range(num_colors)]


def remove_color_from_neighbors(graph, node, color, colors_sets):
    neighbors = list(graph.neighbors(node))
    nodes = list(graph.nodes())
    for neighbor in neighbors:
        index = nodes.index(neighbor)
        if color in colors_sets[index]:
            colors_sets[index].remove(color)


def add_color_to_neighbors(graph, node, color, colors_sets, coloring):
    neighbors = list(graph.neighbors(node))
    nodes = list(graph.nodes())
    flag = True
    for neighbor in neighbors:
        neighbors_for_neighbor = list(graph.neighbors(neighbor))
        for n_f_n in neighbors_for_neighbor:
            index_n_f_n = nodes.index(n_f_n)
            if coloring.get(str(index_n_f_n)) == color and n_f_n not in neighbors:
                flag = False
        if flag:
            index = nodes.index(neighbor)
            if color not in colors_sets[index]:
                colors_sets[index].add(color)


def backtrack_coloring(graph, node_index, max_colors, coloring, colors_sets, counters, n, sorted_node_indices):
    nodes = list(graph.nodes())

    if node_index == len(nodes):
        return True

    node_index_sorted = int(sorted_node_indices[node_index])

    node = nodes[node_index_sorted]

    colors = colors_sets[node_index_sorted].copy()

    for color in colors:
        flag = True
        if n != -1:
            counters[color - 1] = counters[color - 1] + 1
            if not balance_colors(counters, graph.number_of_nodes(), n):
                counters[color - 1] = counters[color - 1] - 1
                flag = False

        if flag:
            if color in colors_sets[node_index_sorted]:
                coloring[node] = color
                old_sets = copy.deepcopy(colors_sets)
                remove_color_from_neighbors(graph, node, color, colors_sets)
                if backtrack_coloring(graph, node_index + 1, max_colors, coloring, colors_sets, counters, n, sorted_node_indices):
                    return True
                if n != -1:
                    counters[color - 1] = counters[color - 1] - 1
                coloring.pop(node)
                #add_color_to_neighbors(graph, node, color, colors_sets, coloring)
                colors_sets = old_sets.copy()
            else:
                if n != -1:
                    counters[color - 1] = counters[color - 1] - 1
    return False


def sorted_nodes_by_degree(graph):
    node_degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes()]
    sorted_nodes = sorted(node_degree, key=lambda x: x[1], reverse=True)
    sorted_node_indices = [node for node, _ in sorted_nodes]

    return sorted_node_indices


def exact_graph_coloring(graph, n):
    num_nodes = len(graph.nodes())
    low, high = 1, num_nodes
    result = num_nodes
    final_coloring = {}
    counters = {}

    sorted_node_indices = sorted_nodes_by_degree(graph)

    while low <= high:
        mid = (low + high) // 2
        colors_sets = create_color_sets(num_nodes, mid)
        if n != -1:
            counters = create_counter_for_colors(mid)
        print(f"the number of colors is changed to {mid}")
        coloring = {}

        if backtrack_coloring(graph, 0, mid, coloring, colors_sets, counters, n, sorted_node_indices):
            result = mid
            final_coloring = coloring.copy()
            high = mid - 1
            print(f"the coloring is possible with {mid} colors")
        else:
            low = mid + 1
            print(f"the coloring is NOT possible with {mid} colors")

    return result, final_coloring
