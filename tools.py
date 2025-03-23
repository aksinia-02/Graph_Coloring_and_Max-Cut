import matplotlib.pyplot as plt
import networkx as nx

def display_graph(G):
    plt.figure(figsize=(6, 6))
    nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500)
    plt.show()


def display_colored_graph(G, coloring, color_map):
    """Display the graph with nodes colored based on the assigned coloring."""

    # Get the node colors based on the coloring dictionary and color map
    node_colors = [color_map[coloring.get(node, 1)] for node in G.nodes()]

    plt.figure(figsize=(6, 6))

    # Draw the graph with specified node colors
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