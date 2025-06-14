import networkx as nx
from pyvis.network import Network
import matplotlib.cm as cm
import numpy as np
import csv

def display_colored_graph(G, coloring, color_map, output_file="graph.html"):
    """Display the graph with nodes colored based on the assigned coloring."""

    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

    pos = nx.spring_layout(G, seed=42)

    for node in G.nodes():
        color = color_map.get(coloring.get(node, 1), "#97C2FC")
        x, y = pos[node]
        net.add_node(
            node,
            label=str(node),
            color=color,
            x=x * 1000,
            y=y * 1000,
            physics=False,
            font={'size': 36, 'face': 'arial', 'vadjust': 0}
        )

    for u, v in G.edges():
        net.add_edge(u, v)

    net.set_options(f"""
    {{
        "nodes": {{
            "font": {{
                "size": 36,
                "face": "arial"
            }}
        }},
        "physics": {{
            "enabled": false
        }},
        "edges": {{
            "smooth": false
        }}
    }}
    """)

    net.show(output_file, notebook=False)

def create_color_sets(num_nodes, num_colors):
    return [set(range(1, num_colors + 1)) for _ in range(num_nodes)]

def generate_color_map(m):
    """Generate m distinct colors using a colormap."""
    colors = cm.rainbow(np.linspace(0, 1, m))  # Get m colors from the rainbow colormap
    color_map = {i + 1: "#{:02x}{:02x}{:02x}".format(
        int(colors[i][0] * 255),
        int(colors[i][1] * 255),
        int(colors[i][2] * 255)
    ) for i in range(m)}
    return color_map

def calculate_cut_size(graph, partition):
    cut = [(u, v) for u, v in graph.edges() if partition[u] != partition[v]]
    return len(cut), cut

def read_from_csv_file(filename):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        nodes = next(reader)
        adj_matrix = [list(map(int, row)) for row in reader]

    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    for i, row in enumerate(adj_matrix):
        for j, value in enumerate(row):
            if value:
                graph.add_edge(nodes[i], nodes[j])

    return graph