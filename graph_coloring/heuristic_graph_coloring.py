from collections import Counter
import random

def get_next_uncolored_node(count_sat, count_deg):
    max_sat = max(count_sat.values())

    candidates = [node for node, sat in count_sat.items() if sat == max_sat]

    if len(candidates) > 1:
        candidates.sort(key=lambda node: count_deg[node], reverse=True)

    return candidates[0]


def eq_colored(num_colors, n):
    max_col = max(num_colors.values())
    min_col = min(num_colors.values())
    return max_col - min_col <= n


def calculate_freq(final_coloring, n):
    nodes_count = len(final_coloring)

    color_counts = Counter(final_coloring.values())
    result = {color: count / nodes_count for color, count in color_counts.items()}

    is_equitable = eq_colored(color_counts, n)
    return is_equitable, result

def FJK(graph, final_coloring, n):
    # algorithm FJK for equitable coloring
    # begin
    #     calculate frequency of colors;
    #     while coloring is not equitable:
    #         begin
    #             find vertices colored with the colors of maximal frequency;
    #             if it is possible to change the color of a vertex colored with the color of maximal frequency to color of minimal frequency then
    #                 do it
    #             else assign a new color to some vertex colored with color of maximal frequency;
    #         end
    # end;
    eq_bool, freq = calculate_freq(final_coloring, n)

    while not eq_bool:
        max_freq = max(freq.values())
        min_freq = min(freq.values())

        max_freq_color = [col for col, value in freq.items() if value == max_freq][0]
        min_freq_color = [col for col, value in freq.items() if value == min_freq][0]

        # Try to find a vertex of max_freq_color that can be recolored to min_freq_color
        candidates = [
            node for node, color in final_coloring.items()
            if color == max_freq_color and
               min_freq_color not in {
                   final_coloring.get(neigh)
                   for neigh in graph.neighbors(node)
               }
        ]
        if candidates:
            node_to_recolor = random.choice(candidates)
            final_coloring[node_to_recolor] = min_freq_color
        # If no candidate found, assign a new color to one node of max_freq_color
        else:
            max_color_nodes = [node for node, color in final_coloring.items() if color == max_freq_color]
            if max_color_nodes:
                node = random.choice(max_color_nodes)
                new_color = max(final_coloring.values()) + 1
                final_coloring[node] = new_color

        eq_bool, freq = calculate_freq(final_coloring, n)
    return final_coloring


def heuristic_graph_coloring(graph, n):
    final_coloring = {}
    nodes = graph.nodes()
    count_sat = {node: 0 for node in nodes}
    count_deg = {node: len(list(graph.neighbors(node))) for node in nodes}
    color_classes = {}

    neighbor_colors = {node: set() for node in graph.nodes()}

    while len(final_coloring) < len(nodes):
        node = get_next_uncolored_node(count_sat, count_deg)
        count_sat.pop(node)
        count_deg.pop(node)
        used_colors = {final_coloring[neighbor] for neighbor in graph.neighbors(node) if neighbor in final_coloring}
        color = 1
        while color in used_colors:
            color += 1

        final_coloring[node] = color
        if color in color_classes:
            color_classes[color] += 1
        else:
            color_classes[color] = 1

        for neighbor in graph.neighbors(node):
            if neighbor not in final_coloring:
                count_sat[neighbor] += 1
                neighbor_colors[neighbor].add(color)

    if n != -1:
        final_coloring = FJK(graph, final_coloring, n)


    chromatic_number = max(final_coloring.values())
    return chromatic_number, final_coloring
