from tools import *
import copy


def balance_colors(counters, n_nodes, n, colors_sets):
    # optimisation by available colors
    colored_nodes = sum(counters)
    uncolored_nodes = n_nodes - colored_nodes

    num_colors = len(counters)

    max_counter = max(counters)

    added = 0
    needed = [0] * num_colors
    for i in range(num_colors):
        diff = max_counter - counters[i]
        diff_n = diff - n
        if diff_n > 0:
            added += diff_n
            needed[i] = diff_n
        if added > uncolored_nodes:
            return False

    # Check if enough nodes can actually take the needed colors
    available = {}
    for color_set in colors_sets:
        for color in color_set:
            if color in available:
                available[color] += 1
            else:
                available[color] = 1

    for color_index in range(num_colors):
        if needed[color_index] > available.get(color_index + 1):
            return False

    return True


def create_counter_for_colors(num_colors):
    return [0 for _ in range(num_colors)]


def remove_color_from_neighbors(graph, node, color, colors_sets, count_sat):
    neighbors = list(graph.neighbors(node))
    nodes = list(graph.nodes())
    for neighbor in neighbors:
        index = nodes.index(neighbor)
        if neighbor in count_sat.keys():
            count_sat[neighbor] += 1
        if color in colors_sets[index]:
            colors_sets[index].remove(color)
            if not colors_sets[index]:
                return True

    return False


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


def get_next_uncolored_node(count_sat, count_deg):
    max_sat = max(count_sat.values())

    candidates = [node for node, sat in count_sat.items() if sat == max_sat]

    if len(candidates) > 1:
        candidates.sort(key=lambda node: count_deg[node], reverse=True)

    return candidates[0]


def backtrack_coloring(graph, node_index, max_colors, coloring, colors_sets, counters, n, count_sat, count_deg):
    if node_index == len(graph.nodes()):
        return True
    node = get_next_uncolored_node(count_deg=count_deg, count_sat=count_sat)
    #print(f"count_deg: {count_deg}")
    #print(f"node: {node}")
    #print(colors_sets)

    #colors = colors_sets[node_index_sorted].copy()
    colors = colors_sets[int(node)].copy()

    for color in colors:
        if color not in colors_sets[int(node)]:
            continue

            # Tentative assignment
        coloring[node] = color
        counters[color - 1] += 1

        if n != -1 and not balance_colors(counters, graph.number_of_nodes(), n, colors_sets):
            counters[color - 1] -= 1
            coloring.pop(node)
            continue

        # Backup structures
        old_sets = copy.deepcopy(colors_sets)
        old_sat = copy.deepcopy(count_sat)
        old_deg = copy.deepcopy(count_deg)

        count_sat.pop(node, None)
        count_deg.pop(node, None)

        some_set_empty = remove_color_from_neighbors(graph, node, color, colors_sets, count_sat)

        if some_set_empty:
            counters[color - 1] -= 1
            coloring.pop(node)
            count_sat = old_sat
            count_deg = old_deg
            colors_sets = old_sets
            continue

        if backtrack_coloring(graph, node_index + 1, max_colors, coloring, colors_sets, counters, n, count_sat,
                              count_deg):
            return True

        # Backtrack
        counters[color - 1] -= 1
        coloring.pop(node)
        count_sat = old_sat
        count_deg = old_deg
        colors_sets = old_sets
        if node_index == 0:
            return False
    return False


def sorted_nodes_by_degree(graph):
    node_degree = [(node, len(list(graph.neighbors(node)))) for node in graph.nodes()]
    sorted_nodes = sorted(node_degree, key=lambda x: x[1], reverse=True)
    sorted_node_indices = [node for node, _ in sorted_nodes]

    return sorted_node_indices

#python .\graph_coloring_solver.py -f .\data\n_30_p_30\d_0.26_vKIe7vlm.csv -o 0 -n 0



def exact_graph_coloring(graph, n):
    num_nodes = len(graph.nodes())
    low, high = 1, num_nodes
    result = num_nodes
    final_coloring = {}
    counters = {}
    #
    # neighbors_set = []
    # for neighbor in graph.neighbors(next(iter(graph.nodes))):
    #     neighbor = Node.Node(neighbor, {})
    #     neighbors_set.append(neighbor)
    # node1 = Node.Node(1, neighbors_set)
    # node2 = Node.Node(1, neighbors_set)
    # node1.remove_color_from_neighbors()
    # node1.print_colors_of_neighbors()
    # node2.print_colors_of_neighbors()


    count_sat = {node: 0 for node in graph.nodes()}
    count_deg = {node: len(list(graph.neighbors(node))) for node in graph.nodes()}
    print(count_deg)

    for mid in range(1, num_nodes + 1):
        colors_sets = create_color_sets(num_nodes, mid)
        if n != -1:
            counters = create_counter_for_colors(mid)
        print(f"the number of colors is changed to {mid}")
        coloring = {}

        if backtrack_coloring(graph, 0, mid, coloring, colors_sets, counters, n, count_sat.copy(), count_deg.copy()):
            result = mid
            final_coloring = coloring.copy()
            return mid, final_coloring
        print(f"the coloring is NOT possible with {mid} colors")

    # while low <= high:
    #     mid = (low + high) // 2
    #     colors_sets = create_color_sets(num_nodes, mid)
    #     if n != -1:
    #         counters = create_counter_for_colors(mid)
    #     print(f"the number of colors is changed to {mid}")
    #     coloring = {}
    #
    #     if backtrack_coloring(graph, 0, mid, coloring, colors_sets, counters, n, sorted_node_indices, count_sat, count_deg):
    #         result = mid
    #         final_coloring = coloring.copy()
    #         high = mid - 1
    #         print(f"the coloring is possible with {mid} colors")
    #     else:
    #         low = mid + 1
    #         print(f"the coloring is NOT possible with {mid} colors")

    return result, final_coloring
