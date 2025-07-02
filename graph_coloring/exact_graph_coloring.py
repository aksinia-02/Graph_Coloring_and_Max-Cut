import copy
from graph_coloring.Node import Node


def cal_density(G):
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = 2 * num_edges / num_nodes / (num_nodes - 1)

    return density


def balance_colors(counters, n_nodes, n, available):
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
            # print(f"added {added}, uncolored_nodes {uncolored_nodes}")
            return False

    # Check if enough nodes can actually take the needed colors

    for i in range(num_colors):
        if needed[i] > available[i]:
            return False

    return True


def remove_color_from_neighbors(node, color, nodes):
    removed_colors_nodes = {}
    for neighbor_index in node.neighbors:
        if neighbor_index in nodes:
            neighbor_node = nodes[neighbor_index]
            if color in neighbor_node.available_colors:
                neighbor_node.remove_color(color)
                neighbor_node.saturation += 1
                removed_colors_nodes[neighbor_index] = True
                if not neighbor_node.available_colors:
                    for removed_node_index in removed_colors_nodes:
                        removed_node = nodes[removed_node_index]
                        removed_node.add_color(color)
                        removed_node.saturation -= 1
                    return True, removed_colors_nodes
    return False, removed_colors_nodes


def get_next_uncolored_node(nodes):
    return max(nodes.values(), key=lambda n: (n.saturation, n.degree))


def backtrack_coloring_eq(node_index, coloring, nodes, counters, n, available):
    if node_index == len(coloring) + len(nodes):
        return True

    node = get_next_uncolored_node(nodes)
    colors = list(node.available_colors)

    count_percent = 0

    for color in colors:
        if node_index == 1:
            print(f"Progress: {(count_percent / len(colors)) * 100:.2f}%")
        count_percent = count_percent + 1

        coloring[node.index] = color
        counters[color - 1] += 1

        # Backup structures
        backup_node = copy.deepcopy(node)
        del nodes[node.index]

        empty_found, removed_colors_nodes = remove_color_from_neighbors(node, color, nodes)
        available[color - 1] -= len(removed_colors_nodes)

        if empty_found:
            counters[color - 1] -= 1
            available[color - 1] += len(removed_colors_nodes)
            coloring.pop(node.index)
            nodes[backup_node.index] = backup_node
            continue

        for available_color in backup_node.available_colors:
            available[available_color - 1] -= 1

        if not balance_colors(counters, len(coloring) + len(nodes), n, available):
            counters[color - 1] -= 1
            for available_color in backup_node.available_colors:
                available[available_color - 1] += 1
            coloring.pop(node.index)
            nodes[backup_node.index] = backup_node

            for removed_node_index in removed_colors_nodes:
                removed_node = nodes[removed_node_index]
                removed_node.add_color(color)
                removed_node.saturation -= 1
            available[color - 1] += len(removed_colors_nodes)
            continue
        if backtrack_coloring_eq(node_index + 1, coloring, nodes, counters, n, available):
            return True

        # Backtrack
        counters[color - 1] -= 1
        for available_color in backup_node.available_colors:
            available[available_color - 1] += 1
        coloring.pop(node.index)
        nodes[backup_node.index] = backup_node

        for removed_node_index in removed_colors_nodes:
            removed_node = nodes[removed_node_index]
            removed_node.add_color(color)
            removed_node.saturation -= 1
        available[color - 1] += len(removed_colors_nodes)
        if node_index == 0:
            return False
    return False


def backtrack_coloring(node_index, coloring, nodes):
    if node_index == len(coloring) + len(nodes):  # total nodes reached
        return True

    node = get_next_uncolored_node(nodes)
    colors = list(node.available_colors)

    count_percent = 0

    for color in colors:
        if node_index == 1:
            print(f"Progress: {(count_percent / len(colors)) * 100:.2f}%")
        count_percent = count_percent + 1

        coloring[node.index] = color

        # Backup structures
        backup_node = copy.deepcopy(node)
        del nodes[node.index]

        empty_found, removed_colors_nodes = remove_color_from_neighbors(node, color, nodes)

        if empty_found:
            coloring.pop(node.index)
            nodes[backup_node.index] = backup_node
            continue

        if backtrack_coloring(node_index + 1, coloring, nodes):
            return True

        # Backtrack
        coloring.pop(node.index)
        nodes[backup_node.index] = backup_node

        for removed_node_index in removed_colors_nodes:
            removed_node = nodes[removed_node_index]
            removed_node.add_color(color)
            removed_node.saturation -= 1
        if node_index == 0:
            return False
    return False


# python .\graph_coloring_solver.py -f ..\data\n_30_p_30\d_0.26_vKIe7vlm.csv -o 0 -n 0
# python .\graph_coloring_solver.py -f .\data\n_200_p_10\d_0.1_1VGDCXqC.csv -o 1 -n 1


def exact_graph_coloring(graph, n, min_num_colors, max_num_colors):
    num_nodes = len(graph.nodes())
    low, high = 1, num_nodes
    if min_num_colors:
        print(f"Minimum number of colors is found from previous run: {min_num_colors}")
        low = min_num_colors
    if max_num_colors:
        print(f"Maximum number of colors is found from previous run: {max_num_colors}")
        high = max_num_colors
    result = num_nodes
    final_coloring = {}

    if n != -1:
        print("Iterative search is used")
        color_range = range(low, high + 1)
        if n == 0:
            numbers_col = []
            for i in color_range:
                if num_nodes % i == 0:
                    numbers_col.append(i)
            color_range = list(numbers_col)

        for mid in color_range:
            color_sets = [set(range(1, mid + 1)) for _ in range(num_nodes)]
            counters = [0] * mid if n != -1 else None
            print(f"the number of colors is changed to {mid}")
            nodes = {}
            for i, node in enumerate(graph.nodes()):
                neighbors = list(graph.neighbors(node))
                nodes[node] = Node(index=node, neighbors=neighbors, available_colors=color_sets[i])

            coloring = {}

            available = [0] * mid
            for node in nodes.values():
                for color in node.available_colors:
                    available[color - 1] += 1
            if n != -1:
                success = backtrack_coloring_eq(0, coloring, nodes, counters, n, available)
            else:
                success = backtrack_coloring(0, coloring, nodes)

            if success:
                final_coloring = coloring.copy()
                print(f"The coloring is possible with {mid} colors")
                return mid, final_coloring
            else:
                print(f"The coloring is NOT possible with {mid} colors")
    else:
        print("Binary search is used")
        while low <= high:
            mid = (low + high) // 2
            color_sets = [set(range(1, mid + 1)) for _ in range(num_nodes)]
            counters = [0] * mid if n != -1 else None
            print(f"the number of colors is changed to {mid}")
            nodes = {}
            for i, node in enumerate(graph.nodes()):
                neighbors = list(graph.neighbors(node))
                nodes[node] = Node(index=node, neighbors=neighbors, available_colors=color_sets[i])

            coloring = {}

            available = [0] * mid
            for node in nodes.values():
                for color in node.available_colors:
                    available[color - 1] += 1

            if n != -1:
                success = backtrack_coloring_eq(0, coloring, nodes, counters, n, available)
            else:
                success = backtrack_coloring(0, coloring, nodes)

            if success:
                result = mid
                final_coloring = coloring.copy()
                high = mid - 1
                print(f"The coloring is possible with {mid} colors")
            else:
                low = mid + 1
                print(f"the coloring is NOT possible with {mid} colors")
    return result, final_coloring
