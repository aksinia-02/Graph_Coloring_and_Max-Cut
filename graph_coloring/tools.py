import matplotlib.pyplot as plt
import networkx as nx

def display_graph(G):
    plt.figure(figsize=(6, 6))
    nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500)
    plt.show()


def display_colored_graph(G, coloring, color_map, output_file="graph.html"):
    """Display the graph with nodes colored based on the assigned coloring."""

    node_colors = [color_map[coloring.get(node, 1)] for node in G.nodes()]

    plt.figure(figsize=(6, 6))

    nx.draw(G, with_labels=True, node_color=node_colors, edge_color='gray', node_size=500, font_size=12,
            font_weight='bold')

    plt.show()

def visualize_colors(color_map):
    """Visualize a dictionary of colors."""
    fig, ax = plt.subplots(figsize=(len(color_map), 1))
    ax.set_xticks([])
    ax.set_yticks([])

    # Create a colored rectangle for each color
    for i, (key, color) in enumerate(color_map.items()):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))

    ax.set_xlim(0, len(color_map))
    ax.set_ylim(0, 1)
    plt.show()

def create_color_sets(num_nodes, num_colors):
    return [set(range(1, num_colors + 1)) for _ in range(num_nodes)]

def print_neighbors(G):
    for node in G.nodes:
        neighbors = G.neighbors(node)
        result =""
        for neighbor in neighbors:
            result += neighbor
            result += ","
        print(f"node: {node}, neighbors: {result}")
        print("")