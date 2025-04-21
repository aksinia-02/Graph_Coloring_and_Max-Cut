# Graph Coloring And Max-Cut

The goal of this project is to study the impact of the number of colors and balanced partitioning constraints—such as those seen in equitable graph coloring and problems similar to graph bisection—on classical graph optimization problems like Graph Coloring and Max-Cut.

## Graph Generation

For this study, a custom random graph generator was created for sparse graphs. The networkx library was used, specifically the erdos_renyi_graph method, which generates a random graph with:

- n nodes

- each possible edge appears independently with probability p

Since erdos_renyi_graph can generate disconnected graphs, the random_graph_generator.py script randomly adds edges to connect any disconnected components, then removes some edges to maintain the graph’s sparsity. The script saves the generated graphs in the data/n_{n}_p_{p} folder, where n is the number of nodes and p is the probability (between 0 and 100) that an edge exists between nodes.

### Options

Generate the sparse random graphs.

options:
  -h, --help            show this help message and exit
  -n, --graphs GRAPHS   The number of graphs.
  -nd, --nodes NODES [NODES ...]
                        The number of nodes. You can use array or single value.
  -p, --probabilities PROBABILITIES [PROBABILITIES ...]
                        The probability that edge between between nodes exists. You can use array or single value between 0 and 1.


## Equitable Graph Coloring

