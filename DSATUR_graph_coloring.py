from tools import *


def get_next_uncolored_node(count_sat, count_deg):
    max_sat = max(count_sat.values())

    candidates = [node for node, sat in count_sat.items() if sat == max_sat]

    if len(candidates) > 1:
        candidates.sort(key=lambda node: count_deg[node], reverse=True)

    return candidates[0]


def dsatur_graph_coloring(graph, n):
    final_coloring = {}
    # final_coloring = {node: 1 for node in graph.nodes()}
    nodes = graph.nodes()
    count_sat = {node: 0 for node in nodes}
    count_deg = {node: len(list(graph.neighbors(node))) for node in nodes}
    color_classes = {}

    neighbor_colors = {node: set() for node in graph.nodes()}

    while len(final_coloring) < len(nodes):
        node = get_next_uncolored_node(count_sat, count_deg)
        #print(f"node: {node}")
        count_sat.pop(node)
        count_deg.pop(node)
        used_colors = {final_coloring[neighbor] for neighbor in graph.neighbors(node) if neighbor in final_coloring}
        #print(f"used_colors: {used_colors}")
        color = 1
        if n == -1:
            while color in used_colors:
                color += 1
        else:
            min_diff = float('inf')
            available_colors = set(range(1, len(nodes) + 1)) - neighbor_colors[node]
            #print(f"available_colors: {available_colors}")
            used_before = {color for color in available_colors if color in color_classes}
            #print(f"used_before: {used_before}")
            new_colors = available_colors - used_before
            #print(f"new_colors: {new_colors}")

            for candidate_color in used_before:
                max_diff = abs(color_classes.get(candidate_color, 0) + 1 - min(color_classes.values(), default=0))
                if max_diff < min_diff:
                    min_diff = max_diff
                    color = candidate_color
            if min_diff > n:
                color = sorted(new_colors)[0]
            #print(f"color: {color}")

        final_coloring[node] = color
        if color in color_classes:
            color_classes[color] += 1
        else:
            color_classes[color] = 1

        for neighbor in graph.neighbors(node):
            if neighbor not in final_coloring:
                count_sat[neighbor] += 1
                neighbor_colors[neighbor].add(color)



    chromatic_number = max(final_coloring.values())

    return chromatic_number, final_coloring
